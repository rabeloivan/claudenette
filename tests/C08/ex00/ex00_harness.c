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

/*
** Calls the five functions but defines none of them - they live in
** ex00_impl.c, a separate translation unit. That separation IS the test:
** with nothing but ft.h in scope here, every prototype the subject requires
** ("It should contain the prototypes of all the following functions") must
** actually be present in the student's header or this file will not compile
** under -Werror. Merging the definitions back into this file would make the
** prototypes unnecessary again and silently un-test the entire exercise.
*/

#include "ft.h"
#include <unistd.h>

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
