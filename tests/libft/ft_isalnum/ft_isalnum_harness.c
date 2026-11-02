#include <stdlib.h>
#include <unistd.h>

int	ft_isalnum(int c);

/* argv[1]..argv[2] is an inclusive codepoint range. One digit is printed per
 * value, so a single comparison covers the whole domain the subject defines
 * rather than a handful of sampled characters. The subject is explicit that
 * the return value must be 1 or 0, not merely zero/non-zero, so the digit is
 * the return value itself and a student returning e.g. 1024 fails here. */
int	main(int argc, char **argv)
{
	int		c;
	int		start;
	int		end;
	char	digit;

	if (argc != 3)
		return (1);
	start = atoi(argv[1]);
	end = atoi(argv[2]);
	c = start;
	while (c <= end)
	{
		digit = '0' + (ft_isalnum(c) ? 1 : 0);
		if (ft_isalnum(c) != 0 && ft_isalnum(c) != 1)
			digit = '?';
		write(1, &digit, 1);
		c++;
	}
	return (0);
}
