/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ex01_harness.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: rabeloivan <rabeloivan@student.42.fr>      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/02/19 16:28:50 by rabeloivan        #+#    #+#             */
/*   Updated: 2026/02/19 16:28:51 by rabeloivan       ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <stdio.h>
#include <string.h>

void	ft_ultimate_ft(int *********nbr);

int	main(int argc, char **argv)
{
	int	nbr;
	int	*ptr1;
	int	**ptr2;
	int	***ptr3;
	int	****ptr4;
	int	*****ptr5;
	int	******ptr6;
	int	*******ptr7;
	int	********ptr8;
	int	*********ptr9;

	if (argc > 1 && strcmp(argv[1], "null_nbr") == 0)
	{
		ft_ultimate_ft(NULL);
		printf("OK");
		return (0);
	}
	ptr1 = &nbr;
	ptr2 = &ptr1;
	ptr3 = &ptr2;
	ptr4 = &ptr3;
	ptr5 = &ptr4;
	ptr6 = &ptr5;
	ptr7 = &ptr6;
	ptr8 = &ptr7;
	ptr9 = &ptr8;
	if (scanf("%d", &nbr) == 1)
	{
		ft_ultimate_ft(ptr9);
		printf("%d", nbr);
	}
	return (0);
}
