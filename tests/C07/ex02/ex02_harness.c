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

int	ft_ultimate_range(int **range, int min, int max);

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
	int		min;
	int		max;
	int		*range;
	int		ret;

	bytes_read = read(0, buffer, 63);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	min = atoi(buffer);
	i = 0;
	while (buffer[i] != '\n' && buffer[i] != '\0')
		i++;
	if (buffer[i] == '\n')
		i++;
	max = atoi(buffer + i);
	range = (int *)1;
	ret = ft_ultimate_range(&range, min, max);
	put_int(ret);
	write(1, "|", 1);
	if (range == NULL)
	{
		write(1, "N", 1);
		return (0);
	}
	if (range == (int *)1)
	{
		write(1, "U", 1);
		return (0);
	}
	write(1, "A", 1);
	i = 0;
	while (i < ret)
	{
		if (i > 0)
			write(1, ",", 1);
		put_int(range[i]);
		i++;
	}
	free(range);
	return (0);
}
