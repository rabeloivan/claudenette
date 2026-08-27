#ifndef FREE_TRACKER_H
# define FREE_TRACKER_H

/*
** Ownership tracking for harnesses that must assert a student freed what the
** subject says they own.
**
** Why this exists: several subjects state two separate obligations - e.g.
** C12 ex06's ft_list_clear "removes and frees all links" AND "free_fct is
** used to free each data". A harness that only records which `data` pointers
** free_fct saw will happily pass an implementation that walks the list
** calling free_fct and never frees a single node. That's a real leak the
** grader used to report as 100/100.
**
** How it works: this file defines free(). Because the student's .c and this
** .c are linked into one binary, the linker resolves the student's free()
** calls to this definition rather than libc's - verified on both macOS and
** Linux. (LeakSanitizer would be the obvious alternative but it is not
** supported on macOS, so it can't be the mechanism here.)
**
** Deliberately does NOT forward to the real free: these are short-lived test
** processes where leaking the few hundred bytes a case allocates is
** harmless, and forwarding portably would mean reaching for platform
** specific symbols (__libc_free and friends) that don't exist everywhere.
**
** This file also interposes malloc(), serving it from a static arena filled
** with a non-zero poison byte. That is not a trick - malloc has never
** promised zeroed memory, so any correct program already has to initialise
** what it allocates. It matters because the real allocator hands back
** freshly-zeroed pages, which silently masks a whole class of bug: a
** ft_split that never writes the NULL terminator the subject requires
** ("The last element of the array should be NULL") passed 5 runs out of 5,
** because the slot it forgot to set happened to already be zero. Under
** poison it fails, deterministically, as it should.
*/

/* Record a pointer the student is expected to free exactly once. */
void	h_track(void *ptr);

/* Forget every tracked pointer - call between independent test cases. */
void	h_track_reset(void);

/* Tracked pointers never passed to free(). */
int		h_leaked_count(void);

/* Tracked pointers passed to free() more than once. */
int		h_double_freed_count(void);

/* Tracked pointers freed exactly once. */
int		h_freed_count(void);

/*
** How many times one specific tracked pointer was freed. Needed where the
** obligation is per-node rather than global - e.g. C12 ex12's
** ft_list_remove_if must free the links it removes and must NOT free the
** ones it keeps, so an aggregate count can't tell a correct implementation
** from one that frees the wrong nodes.
*/
int		h_free_count_of(void *ptr);

/*
** Number of bytes malloc() has handed out so far. Only useful as a crude
** "did the student allocate at all" signal; the arena never shrinks.
*/
unsigned long	h_alloc_total(void);

/*
** Verify no allocation has been written past its end. Called automatically
** from malloc() and free(), so most overflows surface without a harness
** doing anything; call it explicitly at the end of a harness to also cover
** an overflow that happens after the last allocator interaction.
*/
void			h_check_redzones(void);

#endif
