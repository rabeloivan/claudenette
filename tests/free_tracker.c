#include "free_tracker.h"
/*
** stddef.h, not stdlib.h: we need NULL but must not pull in stdlib's own
** declaration of free() next to our definition of it.
*/
#include <stddef.h>
#include <stdint.h>
/* write() for the reports below, _exit() to stop before the damage spreads. */
#include <unistd.h>

/*
** Goes to stdout on purpose: harnesses compare stdout, so the message both
** fails the case and tells whoever reads the log exactly why, instead of the
** test reporting some inscrutable mismatch. The length is counted, not
** written by hand - the overflow report used to be cut one byte short.
*/
static void	h_die(const char *msg)
{
	unsigned long	len;

	len = 0;
	while (msg[len])
		len++;
	write(1, msg, len);
	_exit(1);
}

/*
** 256 is comfortably above the largest list/tree any harness in this repo
** builds (the biggest test case is 10 elements), so overflowing the table
** means a harness bug rather than a student one. It stops the run saying so:
** it used to stop tracking in silence, which would quietly have made every
** later leak and double free invisible.
*/
#define TRACK_MAX 256

static void	*g_tracked[TRACK_MAX];
static int	g_freed[TRACK_MAX];
static int	g_count;

void	h_track(void *ptr)
{
	if (ptr == NULL)
		return ;
	if (g_count >= TRACK_MAX)
		h_die("\nFREE TRACKER FULL: a claudenette harness tracks more than "
			"256 pointers\n");
	g_tracked[g_count] = ptr;
	g_freed[g_count] = 0;
	g_count++;
}

void	h_track_reset(void)
{
	g_count = 0;
}

/*
** Interposes libc's free for every call made from anywhere in this binary.
** A pointer we aren't tracking is ignored rather than forwarded - see the
** header for why not forwarding is safe here.
**
** A pointer inside the arena that no malloc returned - `free(str + 1)`, a
** pointer into the middle of a block - stops the run: libc aborts on it
** ("free(): invalid pointer"), and it used to be ignored here. One from
** outside the arena is left alone: on macOS, memory libc allocates for
** itself (strdup's, say) never passes through this malloc at all.
**
** free(NULL) is explicitly a no-op in C, so it must not count as freeing
** anything: an implementation that ends with free(begin_list) once the
** loop has already walked begin_list to NULL is exactly the bug this
** tracker exists to catch, and forgiving it here would defeat the purpose.
**
** The block is not returned to anyone, but it is scribbled (see
** h_scribble): a block that kept its old bytes let the classic
** `free(node); node = node->next;` walk a whole list correctly, where
** glibc's tcache overwrites `next` and the real run dies.
*/
static int	h_scribble(void *ptr);
static int	h_in_arena(void *ptr);

void	free(void *ptr)
{
	int	i;

	h_check_redzones();
	if (ptr == NULL)
		return ;
	if (!h_scribble(ptr) && h_in_arena(ptr))
		h_die("\nINVALID FREE: free() of a pointer malloc never returned\n");
	i = 0;
	while (i < g_count)
	{
		if (g_tracked[i] == ptr)
		{
			g_freed[i]++;
			return ;
		}
		i++;
	}
}

int	h_leaked_count(void)
{
	int	i;
	int	n;

	i = 0;
	n = 0;
	while (i < g_count)
	{
		if (g_freed[i] == 0)
			n++;
		i++;
	}
	return (n);
}

int	h_double_freed_count(void)
{
	int	i;
	int	n;

	i = 0;
	n = 0;
	while (i < g_count)
	{
		if (g_freed[i] > 1)
			n++;
		i++;
	}
	return (n);
}

int	h_free_count_of(void *ptr)
{
	int	i;

	i = 0;
	while (i < g_count)
	{
		if (g_tracked[i] == ptr)
			return (g_freed[i]);
		i++;
	}
	return (-1);
}

/*
** Interposed malloc. Once this symbol exists in the binary every allocation
** in it - the harness's own included - comes here, so the arena has to
** serve unconditionally rather than being something we switch on.
**
** 1 MiB is far beyond what any harness in this repo allocates (the largest
** case builds a 10-element list), and running out returns NULL, which is a
** perfectly legal malloc result that correct student code already handles.
**
** POISON is 0xAA rather than 0: the entire point is that memory handed to
** the student must NOT look like it was pre-zeroed, so a missing NULL
** terminator or an uninitialised field shows up instead of hiding.
*/
#define ARENA_SIZE (1024UL * 1024UL)
#define POISON 0xAA
#define ALIGN 16UL
/*
** Guard bytes placed before and after every allocation and checked later. Without them
** a heap overflow that still produces the right output is invisible: the
** real allocator rounds sizes up so a few bytes of slack absorb the write,
** and a bump arena like this one absorbs it even more quietly. C07 ex03's
** ft_strjoin with its separator-length term deleted under-allocates by
** strlen(sep) * (size - 1) bytes, writes past the end, prints exactly the
** right string, and used to score OK.
*/
#define REDZONE 16
#define GUARD 0x5C
/*
** A slot for every block the arena can hold: even malloc(0) consumes at least
** ALIGN bytes of it (its redzones), so there can never be more than
** ARENA_SIZE / ALIGN. The table used to share TRACK_MAX's 256 and stop
** recording without a word - an overflow in the 257th block went unseen,
** and freeing it was never scribbled.
*/
#define BLOCK_MAX (ARENA_SIZE / ALIGN)

_Alignas(16) static unsigned char	g_arena[ARENA_SIZE];
static unsigned long	g_arena_used;
static unsigned char	*g_blocks[BLOCK_MAX];
static unsigned long	g_sizes[BLOCK_MAX];
static unsigned char	g_released[BLOCK_MAX];
static int				g_block_count;
static int				g_scope_start;
static int				g_inject;
static int				g_paused;
static long				g_fail_at;
static long				g_attempts;

void	h_alloc_begin(long fail_at)
{
	g_scope_start = g_block_count;
	g_fail_at = fail_at;
	g_attempts = 0;
	g_paused = 0;
	g_inject = 1;
}

void	h_alloc_stop(void)
{
	g_inject = 0;
}

void	h_alloc_pause(int paused)
{
	g_paused = paused;
}

long	h_alloc_attempts(void)
{
	return (g_attempts);
}

int	h_alloc_live(void)
{
	int	i;
	int	live;

	i = g_scope_start;
	live = 0;
	while (i < g_block_count)
		live += !g_released[i++];
	return (live);
}

void	*h_alloc_base(void *ptr)
{
	int			i;
	uintptr_t	address;
	uintptr_t	base;

	address = (uintptr_t)ptr;
	i = g_scope_start;
	while (i < g_block_count)
	{
		base = (uintptr_t)g_blocks[i];
		if (!g_released[i] && address >= base && address - base < g_sizes[i])
			return (g_blocks[i]);
		i++;
	}
	return (NULL);
}

int	h_alloc_owned(void *ptr)
{
	int	i;

	i = g_scope_start;
	while (i < g_block_count)
	{
		if (g_blocks[i] == ptr)
			return (!g_released[i]);
		i++;
	}
	return (0);
}

static void	h_die_overflow(void)
{
	h_die("\nHEAP OVERFLOW: wrote past the end of a malloc'd block\n");
}

void	h_check_redzones(void)
{
	int				b;
	unsigned long	i;
	unsigned char	*end;

	b = 0;
	while (b < g_block_count)
	{
		i = 0;
		while (i < REDZONE)
		{
			if ((g_blocks[b] - REDZONE)[i] != GUARD)
				h_die("\nHEAP UNDERFLOW: wrote before the start of a malloc'd block\n");
			i++;
		}
		end = g_blocks[b] + g_sizes[b];
		i = 0;
		while (i < REDZONE)
		{
			if (end[i] != GUARD)
				h_die_overflow();
			i++;
		}
		b++;
	}
}

void	*malloc(unsigned long size)
{
	unsigned char	*p;
	unsigned long	i;
	unsigned long	want;

	h_check_redzones();
	if (g_inject && !g_paused)
	{
		g_attempts++;
		if (g_fail_at >= 0 && g_attempts > g_fail_at)
			return (NULL);
	}
	/*
	** malloc(0) is a block of size 0 - a unique pointer that may be freed but
	** not written through - so its guard starts at byte 0. It used to be
	** bumped to 1 byte, and the terminator a C07 ft_strjoin with size == 0
	** wrote into its malloc(0) landed in that byte and passed.
	**
	** The guard starts at exactly the caller's requested size, NOT at the
	** aligned size - otherwise the alignment padding becomes slack a small
	** overflow could hide in, which is the very bug being hunted. Only the
	** *total* consumed is rounded, to keep the next block aligned.
	*/
	/* Reject before addition too: SIZE_MAX must not wrap the guard size. */
	if (size > ARENA_SIZE - 2 * REDZONE - ALIGN)
		return (NULL);
	want = (size + 2 * REDZONE + (ALIGN - 1)) & ~(ALIGN - 1);
	if (want > ARENA_SIZE || g_arena_used + want > ARENA_SIZE)
		return (NULL);
	p = &g_arena[g_arena_used + REDZONE];
	g_arena_used += want;
	i = 0;
	while (i < size)
	{
		p[i] = POISON;
		i++;
	}
	i = 0;
	while (i < REDZONE)
	{
		(p - REDZONE)[i] = GUARD;
		p[size + i] = GUARD;
		i++;
	}
	if (g_block_count < (int)BLOCK_MAX)
	{
		g_blocks[g_block_count] = p;
		g_sizes[g_block_count] = size;
		g_block_count++;
	}
	return ((void *)p);
}

/*
** Overwrite a freed block with a byte no pointer or string is made of. Any
** read through a freed node - `node->next`, `node->data` - then yields
** 0x5555555555555555, which faults when dereferenced, instead of the value
** the student is no longer entitled to. macOS's MallocScribble fills freed
** memory with the same 0x55, and glibc clobbers the first 16 bytes with its
** tcache bookkeeping, so the real moulinette fails such code too.
**
** Only blocks this arena handed out are touched; a pointer from anywhere
** else is left alone. Returns whether ptr was such a block.
*/
static int	h_scribble(void *ptr)
{
	int				b;
	unsigned long	i;

	b = 0;
	while (b < g_block_count)
	{
		if (g_blocks[b] == ptr)
		{
			if (g_released[b])
				h_die("\nDOUBLE FREE: block already freed\n");
			g_released[b] = 1;
			i = 0;
			while (i < g_sizes[b])
				g_blocks[b][i++] = 0x55;
			return (1);
		}
		b++;
	}
	return (0);
}

/* Compared as integers: < between unrelated pointers is undefined in C. */
static int	h_in_arena(void *ptr)
{
	return ((unsigned long)ptr - (unsigned long)g_arena < ARENA_SIZE);
}

unsigned long	h_alloc_total(void)
{
	return (g_arena_used);
}

int	h_freed_count(void)
{
	int	i;
	int	n;

	i = 0;
	n = 0;
	while (i < g_count)
	{
		if (g_freed[i] == 1)
			n++;
		i++;
	}
	return (n);
}
