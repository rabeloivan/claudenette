/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ex00_impl.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: claudenette <claudenette@student.42.fr>    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/26 00:00:00 by claudenette       #+#    #+#             */
/*   Updated: 2026/08/26 00:00:00 by claudenette      ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

/*
** The five functions ft.h is required to declare, defined in a translation
** unit of their own.
**
** This file deliberately does NOT include ft.h. The whole exercise is "your
** header should contain the prototypes of all the following functions", so
** the only way to test that is to make the *caller* depend on those
** prototypes and nothing else. When the definitions lived alongside main() in
** ex00_harness.c they were declared before use by virtue of being defined
** above it, the prototypes were never needed, and a student could turn in an
** ft.h holding nothing but an include guard and still score 100/100 - which
** it did.
**
** Keep these definitions here and the calls in ex00_harness.c, or that hole
** reopens silently.
*/

#include <unistd.h>

void	ft_putchar(char c)
{
	write(1, &c, 1);
}

void	ft_swap(int *a, int *b)
{
	int	tmp;

	tmp = *a;
	*a = *b;
	*b = tmp;
}

void	ft_putstr(char *str)
{
	while (*str)
		write(1, str++, 1);
}

int	ft_strlen(char *str)
{
	int	i;

	i = 0;
	while (str[i])
		i++;
	return (i);
}

int	ft_strcmp(char *s1, char *s2)
{
	int	i;

	i = 0;
	while (s1[i] && s1[i] == s2[i])
		i++;
	return ((unsigned char)s1[i] - (unsigned char)s2[i]);
}
