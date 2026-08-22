/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ex04_harness.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: rabeloivan <rabeloivan@student.42.fr>      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/02/19 16:27:18 by rabeloivan        #+#    #+#             */
/*   Updated: 2026/02/19 16:27:19 by rabeloivan       ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <unistd.h>
#include <stdlib.h>

void	ft_is_negative(int n);

int	main(void)
{
	char	buffer[50];
	int		bytes_read;

	bytes_read = read(0, buffer, 49);
	if (bytes_read > 0)
	{
		buffer[bytes_read] = '\0';
		ft_is_negative(atoi(buffer));
	}
	return (0);
}
