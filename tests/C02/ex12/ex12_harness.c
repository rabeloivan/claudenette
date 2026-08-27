#include <unistd.h>

void	*ft_print_memory(void *addr, unsigned int size);

int	main(void)
{
	char			buffer[4096];
	int				bytes_read;
	unsigned int	size;
	int				i;
	void			*ret;
	char			marker;

	bytes_read = read(0, buffer, 4095);
	if (bytes_read < 0)
		return (0);
	i = 0;
	size = 0;
	while (buffer[i] >= '0' && buffer[i] <= '9')
	{
		size = size * 10 + (buffer[i] - '0');
		i++;
	}
	if (buffer[i] == '\n')
		i++;
	ret = ft_print_memory(buffer + i, size);
	if (ret == (void *)(buffer + i))
		marker = '1';
	else
		marker = '0';
	write(1, &marker, 1);
	write(1, "\n", 1);
	return (0);
}
