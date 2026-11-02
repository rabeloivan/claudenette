#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "../../free_tracker.h"

char	**ft_split(char *str, char *charset);

int	main(void)
{
	char	buffer[4096];
	char	str[2048];
	char	original[2048];
	char	*charset;
	int		bytes_read;
	int		i;
	int		str_len;
	int		j;
	char	**ret;
	int		k;

	bytes_read = read(0, buffer, 4095);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	i = 0;
	str_len = 0;
	while (buffer[i] >= '0' && buffer[i] <= '9')
	{
		str_len = str_len * 10 + (buffer[i] - '0');
		i++;
	}
	if (buffer[i] == '\n')
		i++;
	j = 0;
	while (j < str_len)
	{
		str[j] = buffer[i + j];
		j++;
	}
	str[j] = '\0';
	charset = buffer + i + str_len;
	memcpy(original, str, str_len + 1);
	ret = ft_split(str, charset);
	if (memcmp(original, str, str_len + 1))
		return (write(1, "MUTATED INPUT", 13), 0);
	if (ret == NULL)
	{
		write(1, "N", 1);
		return (0);
	}
	write(1, "A", 1);
	k = 0;
	while (ret[k] != NULL)
	{
		if (k > 0)
			write(1, "\x01", 1);
		write(1, ret[k], strlen(ret[k]));
		k++;
	}
	/* C07/C09 allow only malloc and do not specify per-word freeability.
	 * Unlike Libft 19.3, a single allocation containing all words is valid.
	 * This short-lived probe checks writes, not an invented cleanup layout. */
	h_check_redzones();
	return (0);
}
