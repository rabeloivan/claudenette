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

int	ft_atoi_base(char *str, char *base);

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
	char	buffer[4096];
	char	base[256];
	char	*str;
	int		bytes_read;
	int		i;
	int		j;
	int		base_len;
	int		ret;

	bytes_read = read(0, buffer, 4095);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	i = 0;
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
	str = buffer + i + base_len;
	ret = ft_atoi_base(str, base);
	put_int(ret);
	return (0);
}
