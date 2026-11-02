#include "libft_ref.h"

char	*ft_strrchr(const char *s, int c)
{
	size_t	i;

	i = ft_strlen(s);
	if ((char)c == '\0')
		return ((char *)(s + i));
	while (i-- > 0)
	{
		if (s[i] == (char)c)
			return ((char *)(s + i));
	}
	return (NULL);
}
