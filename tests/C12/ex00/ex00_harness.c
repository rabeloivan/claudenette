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

#include "ft_list.h"
#include "../harness_utils.h"
#include <stdlib.h>
#include <unistd.h>

t_list	*ft_create_elem(void *data);

int	main(void)
{
	char	buffer[64];
	int		bytes_read;
	int		value;
	t_list	*elem;

	bytes_read = read(0, buffer, 63);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	value = atoi(buffer);
	elem = ft_create_elem((void *)(long)value);
	if (elem == NULL)
	{
		write(1, "N", 1);
		return (0);
	}
	write(1, "A", 1);
	h_put_int((int)(long)elem->data);
	write(1, "|", 1);
	if (elem->next == NULL)
		write(1, "1", 1);
	else
		write(1, "0", 1);
	return (0);
}
