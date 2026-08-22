/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ex04_harness.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: rabeloivan <rabeloivan@student.42.fr>      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/16 00:00:00 by rabeloivan        #+#    #+#             */
/*   Updated: 2026/08/16 00:00:00 by rabeloivan       ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <stdlib.h>
#include <unistd.h>

void	ft_putnbr_base(int nbr, char *base);

int	main(void)
{
	char	buffer[4096];
	char	base[256];
	int		bytes_read;
	int		i;
	int		j;
	int		nbr;
	int		base_len;

	bytes_read = read(0, buffer, 4095);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	nbr = atoi(buffer);
	i = 0;
	while (buffer[i] != '\n' && buffer[i] != '\0')
		i++;
	if (buffer[i] == '\n')
		i++;
	base_len = 0;
	while (buffer[i] >= '0' && buffer[i] <= '9')
	{
		base_len = base_len * 10 + (buffer[i] - '0');
		i++;
	}
	if (buffer[i] == '\n')
		i++;
	j = 0;
	while (j < base_len)
	{
		base[j] = buffer[i + j];
		j++;
	}
	base[j] = '\0';
	ft_putnbr_base(nbr, base);
	return (0);
}
