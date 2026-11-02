#include <stdlib.h>
#include <unistd.h>

#include "../../free_tracker.h"

char	**ft_split(char const *s, char c);

size_t	ft_strlen(const char *s);

static void	put_size(size_t n)
{
	char	c;

	if (n >= 10)
		put_size(n / 10);
	c = '0' + (n % 10);
	write(1, &c, 1);
}

/* Prints every element bracketed, then |<count>.
 *
 * Iteration stops on the array's NULL terminator, which is the entire point:
 * linked against free_tracker.c, malloc hands back 0xAA rather than zeroed
 * pages, so a split that fills the array but never writes the final NULL runs
 * off the end instead of stopping on a byte that happened to be zero. That
 * exact bug passed 5 runs out of 5 before the poisoned arena existed. */
int	main(int argc, char **argv)
{
	char	**parts;
	size_t	i;
	size_t	j;
	char	*original;

	if (argc != 3)
		return (1);
	original = malloc(ft_strlen(argv[1]) + 1);
	if (!original)
		return (1);
	i = 0;
	while ((original[i] = argv[1][i]) != '\0')
		i++;
	h_alloc_begin(-1);
	parts = ft_split(argv[1], argv[2][0]);
	h_alloc_stop();
	if (!parts)
		return (write(1, "NULL", 4), 0);
	i = 0;
	while (original[i] == argv[1][i] && original[i])
		i++;
	if (original[i] != argv[1][i] || !h_alloc_owned(parts))
		return (write(1, "BAD SOURCE OR ARRAY", 19), 0);
	i = 0;
	while (parts[i])
	{
		/* Each word must be independently allocated and freeable (Part 2). */
		if (!h_alloc_owned(parts[i]))
			return (write(1, "BAD WORD OWNERSHIP", 18), 0);
		j = 0;
		while (j < i)
			if (parts[j++] == parts[i])
				return (write(1, "SHARED WORD", 11), 0);
		write(1, "[", 1);
		write(1, parts[i], ft_strlen(parts[i]));
		write(1, "]", 1);
		i++;
		if (i > 64)
			return (write(1, "|RUNAWAY", 8), 0);
	}
	write(1, "|", 1);
	put_size(i);
	j = 0;
	while (j < i)
		free(parts[j++]);
	free(parts);
	if (h_alloc_live())
		write(1, "LEAK", 4);
	free(original);
	h_check_redzones();
	return (0);
}
