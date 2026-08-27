#include "free_tracker.h"
/*
** stddef.h, not stdlib.h: we need NULL but must not pull in stdlib's own
** declaration of free() next to our definition of it.
*/
#include <stddef.h>
/* write() for the overflow report, _exit() to stop before the damage spreads. */
#include <unistd.h>

/*
** 256 is comfortably above the largest list/tree any harness in this repo
** builds (the biggest test case is 10 elements), so overflowing the table
** would mean a harness bug rather than a student one - a pointer that
** doesn't fit is simply not tracked, which can only ever make the grader
** more lenient, never wrongly fail someone.
*/
#define TRACK_MAX 256

static void	*g_tracked[TRACK_MAX];
static int	g_freed[TRACK_MAX];
static int	g_count;

void	h_track(void *ptr)
{
	if (ptr == NULL || g_count >= TRACK_MAX)
		return ;
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
** free(NULL) is explicitly a no-op in C, so it must not count as freeing
** anything: an implementation that ends with free(begin_list) once the
** loop has already walked begin_list to NULL is exactly the bug this
** tracker exists to catch, and forgiving it here would defeat the purpose.
*/
void	free(void *ptr)
{
	int	i;

	h_check_redzones();
	if (ptr == NULL)
		return ;
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
** Guard bytes placed after every allocation and checked later. Without them
** a heap overflow that still produces the right output is invisible: the
** real allocator rounds sizes up so a few bytes of slack absorb the write,
** and a bump arena like this one absorbs it even more quietly. C07 ex03's
** ft_strjoin with its separator-length term deleted under-allocates by
** strlen(sep) * (size - 1) bytes, writes past the end, prints exactly the
** right string, and used to score OK.
*/
#define REDZONE 16
#define GUARD 0x5C

static unsigned char	g_arena[ARENA_SIZE];
static unsigned long	g_arena_used;
static unsigned char	*g_blocks[TRACK_MAX];
static unsigned long	g_sizes[TRACK_MAX];
static int				g_block_count;

static void	h_die_overflow(void)
{
	/*
	** Goes to stdout on purpose: harnesses compare stdout, so this both
	** fails the case and tells whoever reads the log exactly why, instead
	** of the test reporting some inscrutable mismatch.
	*/
	write(1, "\nHEAP OVERFLOW: wrote past the end of a malloc'd block\n", 54);
	_exit(1);
}

void	h_check_redzones(void)
{
	int				b;
	unsigned long	i;
	unsigned char	*end;

	b = 0;
	while (b < g_block_count)
	{
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
	if (size == 0)
		size = 1;
	/*
	** The guard starts at exactly the caller's requested size, NOT at the
	** aligned size - otherwise the alignment padding becomes slack a small
	** overflow could hide in, which is the very bug being hunted. Only the
	** *total* consumed is rounded, to keep the next block aligned.
	*/
	want = (size + REDZONE + (ALIGN - 1)) & ~(ALIGN - 1);
	if (want > ARENA_SIZE || g_arena_used + want > ARENA_SIZE)
		return (NULL);
	p = &g_arena[g_arena_used];
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
		p[size + i] = GUARD;
		i++;
	}
	if (g_block_count < TRACK_MAX)
	{
		g_blocks[g_block_count] = p;
		g_sizes[g_block_count] = size;
		g_block_count++;
	}
	return ((void *)p);
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
