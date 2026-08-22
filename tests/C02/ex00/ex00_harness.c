/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ex00_harness.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: rabeloivan <rabeloivan@student.42.fr>      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/16 00:00:00 by rabeloivan        #+#    #+#             */
/*   Updated: 2026/08/16 00:00:00 by rabeloivan       ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <unistd.h>

#define DUMP_LEN 512

char	*ft_strcpy(char *dest, char *src);

int	main(void)
{
	char	src[4096];
	char	dest[DUMP_LEN];
	int		bytes_read;
	char	*ret;
	char	marker;
	int		i;

	bytes_read = read(0, src, 4095);
	if (bytes_read < 0)
		return (0);
	src[bytes_read] = '\0';
	i = 0;
	while (i < DUMP_LEN)
	{
		dest[i] = (char)0xFF;
		i++;
	}
	ret = ft_strcpy(dest, src);
	if (ret == dest)
		marker = '1';
	else
		marker = '0';
	write(1, &marker, 1);
	write(1, dest, DUMP_LEN);
	return (0);
}
