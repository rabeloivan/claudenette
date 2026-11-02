#include <stdlib.h>

#include "libft_ref.h"

static size_t	count_words(char const *s, char c)
{
	size_t	count;
	size_t	i;

	count = 0;
	i = 0;
	while (s[i])
	{
		while (s[i] == c && s[i])
			i++;
		if (s[i])
			count++;
		while (s[i] != c && s[i])
			i++;
	}
	return (count);
}

static void	free_all(char **parts, size_t filled)
{
	while (filled-- > 0)
		free(parts[filled]);
	free(parts);
}

static int	fill(char **parts, char const *s, char c)
{
	size_t	i;
	size_t	start;
	size_t	word;

	i = 0;
	word = 0;
	while (s[i])
	{
		while (s[i] == c && s[i])
			i++;
		start = i;
		while (s[i] != c && s[i])
			i++;
		if (i > start)
		{
			parts[word] = ft_substr(s, (unsigned int)start, i - start);
			if (!parts[word])
				return (free_all(parts, word), 0);
			word++;
		}
	}
	parts[word] = NULL;
	return (1);
}

char	**ft_split(char const *s, char c)
{
	char	**parts;

	if (!s)
		return (NULL);
	parts = malloc(sizeof(char *) * (count_words(s, c) + 1));
	if (!parts)
		return (NULL);
	if (!fill(parts, s, c))
		return (NULL);
	return (parts);
}
