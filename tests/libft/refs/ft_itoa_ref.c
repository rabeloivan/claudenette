#include <stdlib.h>

#include "libft_ref.h"

static size_t	digits(int n)
{
	size_t	count;

	count = 1;
	if (n < 0)
		count++;
	while (n <= -10 || n >= 10)
	{
		n /= 10;
		count++;
	}
	return (count);
}

char	*ft_itoa(int n)
{
	char	*out;
	size_t	len;

	len = digits(n);
	out = malloc(len + 1);
	if (!out)
		return (NULL);
	out[len] = '\0';
	if (n == 0)
		out[0] = '0';
	if (n < 0)
		out[0] = '-';
	while (n != 0)
	{
		if (n < 0)
			out[--len] = '0' - (n % 10);
		else
			out[--len] = '0' + (n % 10);
		n /= 10;
	}
	return (out);
}
