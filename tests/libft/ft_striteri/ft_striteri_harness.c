#include <stdlib.h>
#include <unistd.h>

void	ft_striteri(char *s, void (*f)(unsigned int, char *));

size_t	ft_strlen(const char *s);

/* The subject is explicit that each character is passed BY ADDRESS "so it can
 * be modified if necessary" - so f writes through the pointer and the test
 * inspects the original buffer afterwards. A student who passes a copy leaves
 * the string unchanged and fails here. */
static int mode;

static void	alternate_case(unsigned int i, char *c)
{
	if (mode) { *c = mode == 1 ? (char)(*c + i) : '0'; return; }
	if (i % 2 == 0)
	{
		if (*c >= 'a' && *c <= 'z')
			*c -= 32;
		return ;
	}
	if (*c >= 'A' && *c <= 'Z')
		*c += 32;
}

int	main(int argc, char **argv)
{
	char	buf[256];
	size_t	i;

	if (argc < 2 || argc > 3)
		return (1);
	i = 0;
	while (argv[1][i] && i < 255)
	{
		buf[i] = argv[1][i];
		i++;
	}
	buf[i] = '\0';
	mode = argc == 3 ? (argv[2][0] == 'a' ? 1 : 2) : 0;
	ft_striteri(buf, alternate_case);
	write(1, buf, ft_strlen(buf));
	return (0);
}
