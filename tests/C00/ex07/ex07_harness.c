/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ex07_harness.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: rabeloivan <rabeloivan@student.42.fr>      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/02/19 16:27:05 by rabeloivan        #+#    #+#             */
/*   Updated: 2026/02/19 16:27:06 by rabeloivan       ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <unistd.h>
#include <stdlib.h>

void	ft_putnbr(int nb);

int	main(void)
{
	char	buffer[50];
	int		bytes_read;

	bytes_read = read(0, buffer, 49);
	if (bytes_read > 0)
	{
		buffer[bytes_read] = '\0';
		ft_putnbr(atoi(buffer));
	}
	return (0);
}
