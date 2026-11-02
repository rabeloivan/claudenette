#include <stdlib.h>
#include <unistd.h>

#include "../../free_tracker.h"

char	*ft_strdup(const char *s1);

size_t	ft_strlen(const char *s);

/* Linked against free_tracker.c: malloc returns 0xAA-poisoned memory, so a
 * duplicate that copies the bytes but forgets the terminator runs off the end
 * into 0xAA instead of stopping at a lucky zero, and the redzone check fires
 * if it under-allocates by even one byte. */
int	main(int argc, char **argv)
{
	char	*dup;

	if (argc != 2)
		return (1);
	dup = ft_strdup(argv[1]);
	if (!dup)
		return (write(1, "NULL", 4), 0);
	if (dup == argv[1])
		return (write(1, "SAMEPTR", 7), 0);
	write(1, dup, ft_strlen(dup));
	h_check_redzones();
	return (0);
}
