/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ex01_harness.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: rabeloivan <rabeloivan@student.42.fr>      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/16 00:00:00 by rabeloivan        #+#    #+#             */
/*   Updated: 2026/08/16 00:00:00 by rabeloivan       ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <unistd.h>

#define DUMP_LEN 512

char	*ft_strncpy(char *dest, char *src, unsigned int n);

int	main(void)
{
	char			buffer[4096];
	char			dest[DUMP_LEN];
	char			*src;
	int				bytes_read;
	unsigned int	n;
	char			*ret;
	char			marker;
	int				i;

	bytes_read = read(0, buffer, 4095);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	i = 0;
	n = 0;
	while (buffer[i] >= '0' && buffer[i] <= '9')
	{
		n = n * 10 + (buffer[i] - '0');
		i++;
	}
	if (buffer[i] == '\n')
		i++;
	src = buffer + i;
	i = 0;
	while (i < DUMP_LEN)
	{
		dest[i] = (char)0xFF;
		i++;
	}
	ret = ft_strncpy(dest, src, n);
	if (ret == dest)
		marker = '1';
	else
		marker = '0';
	write(1, &marker, 1);
	write(1, dest, DUMP_LEN);
	return (0);
}
