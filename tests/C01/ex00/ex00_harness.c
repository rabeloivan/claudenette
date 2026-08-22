/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ex00_harness.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: rabeloivan <rabeloivan@student.42.fr>      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/02/19 16:28:52 by rabeloivan        #+#    #+#             */
/*   Updated: 2026/02/19 16:28:53 by rabeloivan       ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <stdio.h>
#include <string.h>

void	ft_ft(int *nbr);

int	main(int argc, char **argv)
{
	int	nbr;

	if (argc > 1 && strcmp(argv[1], "null_nbr") == 0)
	{
		ft_ft(NULL);
		printf("OK");
		return (0);
	}
	if (scanf("%d", &nbr) == 1)
	{
		ft_ft(&nbr);
		printf("%d", nbr);
	}
	return (0);
}
