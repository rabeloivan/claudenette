#include <stdio.h>
#include <unistd.h>
#include <string.h>

int	ft_strlen(char *str);

int	main(int argc, char **argv)
{
	char	buffer[2048];
	int		bytes_read;

	if (argc > 1 && strcmp(argv[1], "null_str") == 0)
	{
		ft_strlen(NULL);
		printf("OK");
		return (0);
	}
	bytes_read = read(0, buffer, 2047);
	if (bytes_read >= 0)
	{
		buffer[bytes_read] = '\0';
		printf("%d", ft_strlen(buffer));
	}
	return (0);
}
