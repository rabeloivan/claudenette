/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ex04_harness.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: rabeloivan <rabeloivan@student.42.fr>      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/02/19 16:28:43 by rabeloivan        #+#    #+#             */
/*   Updated: 2026/02/19 16:28:43 by rabeloivan       ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <stdio.h>
#include <string.h>

void	ft_ultimate_div_mod(int *a, int *b);

int	main(int argc, char **argv)
{
	int	a;
	int	b;

	if (argc > 1 && strcmp(argv[1], "null_a") == 0)
	{
		b = 3;
		ft_ultimate_div_mod(NULL, &b);
		printf("OK");
		return (0);
	}
	if (argc > 1 && strcmp(argv[1], "null_b") == 0)
	{
		a = 10;
		ft_ultimate_div_mod(&a, NULL);
		printf("OK");
		return (0);
	}
	if (scanf("%d %d", &a, &b) == 2)
	{
		ft_ultimate_div_mod(&a, &b);
		printf("%d %d", a, b);
	}
	return (0);
}
