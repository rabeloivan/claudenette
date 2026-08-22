/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ex05_harness.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: rabeloivan <rabeloivan@student.42.fr>      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/16 00:00:00 by rabeloivan        #+#    #+#             */
/*   Updated: 2026/08/16 00:00:00 by rabeloivan       ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <unistd.h>

#define DUMP_LEN 512

unsigned int	ft_strlcat(char *dest, char *src, unsigned int size);

static void	put_uint_fixed(unsigned int n)
{
	char	digits[10];
	int		i;

	i = 9;
	while (i >= 0)
	{
		digits[i] = '0' + (n % 10);
		n = n / 10;
		i--;
	}
	write(1, digits, 10);
}

int	main(void)
{
	char			buffer[4096];
	char			dest[DUMP_LEN];
	char			*src;
	int				bytes_read;
	int				i;
	int				dest_len;
	int				j;
	unsigned int	size;
	unsigned int	ret;

	bytes_read = read(0, buffer, 4095);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	i = 0;
	size = 0;
	while (buffer[i] >= '0' && buffer[i] <= '9')
	{
		size = size * 10 + (buffer[i] - '0');
		i++;
	}
	if (buffer[i] == '\n')
		i++;
	dest_len = 0;
	while (buffer[i] >= '0' && buffer[i] <= '9')
	{
		dest_len = dest_len * 10 + (buffer[i] - '0');
		i++;
	}
	if (buffer[i] == '\n')
		i++;
	j = 0;
	while (j < DUMP_LEN)
	{
		dest[j] = (char)0xFF;
		j++;
	}
	j = 0;
	while (j < dest_len)
	{
		dest[j] = buffer[i + j];
		j++;
	}
	dest[j] = '\0';
	src = buffer + i + dest_len;
	ret = ft_strlcat(dest, src, size);
	put_uint_fixed(ret);
	write(1, dest, DUMP_LEN);
	return (0);
}
