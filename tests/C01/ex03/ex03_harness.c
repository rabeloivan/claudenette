/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ex03_harness.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: rabeloivan <rabeloivan@student.42.fr>      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/02/19 16:28:45 by rabeloivan        #+#    #+#             */
/*   Updated: 2026/02/19 16:28:46 by rabeloivan       ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <stdio.h>
#include <string.h>

void	ft_div_mod(int a, int b, int *div, int *mod);

int	main(int argc, char **argv)
{
	int	a;
	int	b;
	int	div;
	int	mod;

	if (argc > 1 && strcmp(argv[1], "null_div") == 0)
	{
		ft_div_mod(10, 3, NULL, &mod);
		printf("OK");
		return (0);
	}
	if (argc > 1 && strcmp(argv[1], "null_mod") == 0)
	{
		ft_div_mod(10, 3, &div, NULL);
		printf("OK");
		return (0);
	}
	if (scanf("%d %d", &a, &b) == 2)
	{
		ft_div_mod(a, b, &div, &mod);
		printf("%d %d", div, mod);
	}
	return (0);
}
