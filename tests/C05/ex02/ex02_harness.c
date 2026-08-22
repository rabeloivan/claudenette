/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ex02_harness.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: rabeloivan <rabeloivan@student.42.fr>      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/16 00:00:00 by rabeloivan        #+#    #+#             */
/*   Updated: 2026/08/16 00:00:00 by rabeloivan       ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <stdlib.h>
#include <unistd.h>

int	ft_iterative_power(int nb, int power);

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
	char	buffer[64];
	int		bytes_read;
	int		i;
	int		nb;
	int		power;
	int		ret;

	bytes_read = read(0, buffer, 63);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	nb = atoi(buffer);
	i = 0;
	while (buffer[i] != '\n' && buffer[i] != '\0')
		i++;
	if (buffer[i] == '\n')
		i++;
	power = atoi(buffer + i);
	ret = ft_iterative_power(nb, power);
	put_int(ret);
	return (0);
}
