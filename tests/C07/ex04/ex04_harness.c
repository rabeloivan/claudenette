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
#include <string.h>
#include <unistd.h>

char	*ft_convert_base(char *nbr, char *base_from, char *base_to);

int	main(void)
{
	char	buffer[4096];
	char	nbr[256];
	char	base_from[256];
	char	*base_to;
	int		bytes_read;
	int		i;
	int		nbr_len;
	int		base_from_len;
	int		j;
	char	*ret;

	bytes_read = read(0, buffer, 4095);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	i = 0;
	nbr_len = 0;
	while (buffer[i] >= '0' && buffer[i] <= '9')
	{
		nbr_len = nbr_len * 10 + (buffer[i] - '0');
		i++;
	}
	if (buffer[i] == '\n')
		i++;
	base_from_len = 0;
	while (buffer[i] >= '0' && buffer[i] <= '9')
	{
		base_from_len = base_from_len * 10 + (buffer[i] - '0');
		i++;
	}
	if (buffer[i] == '\n')
		i++;
	j = 0;
	while (j < nbr_len)
	{
		nbr[j] = buffer[i + j];
		j++;
	}
	nbr[j] = '\0';
	i = i + nbr_len;
	j = 0;
	while (j < base_from_len)
	{
		base_from[j] = buffer[i + j];
		j++;
	}
	base_from[j] = '\0';
	i = i + base_from_len;
	base_to = buffer + i;
	ret = ft_convert_base(nbr, base_from, base_to);
	if (ret == NULL)
	{
		write(1, "N", 1);
		return (0);
	}
	write(1, "A", 1);
	write(1, ret, strlen(ret));
	free(ret);
	return (0);
}
