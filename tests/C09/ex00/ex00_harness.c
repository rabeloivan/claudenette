/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ex00_harness.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: rabeloivan <rabeloivan@student.42.fr>      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/16 00:00:00 by rabeloivan        #+#    #+#             */
/*   Updated: 2026/08/16 00:00:00 by rabeloivan       ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <unistd.h>

void	ft_putchar(char c);
void	ft_swap(int *a, int *b);
void	ft_putstr(char *str);
int		ft_strlen(char *str);
int		ft_strcmp(char *s1, char *s2);

static void	put_int(int n)
{
	char	c;

	if (n < 0)
	{
		write(1, "-", 1);
		n = -n;
	}
	if (n >= 10)
		put_int(n / 10);
	c = '0' + (n % 10);
	write(1, &c, 1);
}

int	main(void)
{
	int	a;
	int	b;

	a = 5;
	b = 9;
	ft_putchar('A');
	ft_putstr("BC");
	ft_swap(&a, &b);
	if (a == 9 && b == 5)
		ft_putstr("SWAPOK");
	else
		ft_putstr("SWAPKO");
	put_int(ft_strlen("hello"));
	if (ft_strcmp("abc", "abd") < 0 && ft_strcmp("abd", "abc") > 0
		&& ft_strcmp("abc", "abc") == 0)
		ft_putstr("CMPOK");
	else
		ft_putstr("CMPKO");
	return (0);
}
