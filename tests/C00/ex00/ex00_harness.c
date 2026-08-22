/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ex00_harness.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: rabeloivan <rabeloivan@student.42.fr>      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/02/19 16:27:29 by rabeloivan        #+#    #+#             */
/*   Updated: 2026/02/19 16:27:30 by rabeloivan       ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <unistd.h>

void	ft_putchar(char c);

int	main(void)
{
	char	c;

	while (read(0, &c, 1) > 0)
	{
		ft_putchar(c);
	}
	return (0);
}
