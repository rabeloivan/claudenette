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

#include "ft_list.h"
#include "../harness_utils.h"
#include <stdlib.h>
#include <unistd.h>

void	ft_list_push_back(t_list **begin_list, void *data);

int	main(void)
{
	char	buffer[4096];
	int		bytes_read;
	int		count;
	int		pos;
	int		i;
	t_list	*list;
	t_list	*cur;
	int		value;

	bytes_read = read(0, buffer, 4095);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	count = atoi(buffer);
	pos = 0;
	while (buffer[pos] != '\n')
		pos++;
	pos++;
	list = NULL;
	i = 0;
	while (i < count)
	{
		value = atoi(buffer + pos);
		while (buffer[pos] != ',' && buffer[pos] != '\0')
			pos++;
		if (buffer[pos] == ',')
			pos++;
		ft_list_push_back(&list, (void *)(long)value);
		i++;
	}
	cur = list;
	i = 0;
	while (cur != NULL)
	{
		if (i > 0)
			write(1, ",", 1);
		h_put_int((int)(long)cur->data);
		cur = cur->next;
		i++;
	}
	return (0);
}
