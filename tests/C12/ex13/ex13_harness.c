/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ex13_harness.c                                     :+:      :+:    :+:   */
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

void	ft_list_merge(t_list **begin_list1, t_list *begin_list2);

static int	read_list(char *buffer, int pos, int *count, int *values)
{
	int	i;

	*count = atoi(buffer + pos);
	while (buffer[pos] != '\n' && buffer[pos] != '\0')
		pos++;
	if (buffer[pos] == '\n')
		pos++;
	i = 0;
	while (i < *count)
	{
		values[i] = atoi(buffer + pos);
		while (buffer[pos] != ',' && buffer[pos] != '\n' && buffer[pos] != '\0')
			pos++;
		if (buffer[pos] == ',')
			pos++;
		i++;
	}
	while (buffer[pos] != '\n' && buffer[pos] != '\0')
		pos++;
	if (buffer[pos] == '\n')
		pos++;
	return (pos);
}

int	main(void)
{
	char	buffer[4096];
	int		bytes_read;
	int		pos;
	int		i;
	int		count1;
	int		count2;
	int		values1[64];
	int		values2[64];
	t_list	*list1;
	t_list	*list2;
	t_list	*cur;

	bytes_read = read(0, buffer, 4095);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	pos = read_list(buffer, 0, &count1, values1);
	read_list(buffer, pos, &count2, values2);
	list1 = h_build_list(values1, count1);
	list2 = h_build_list(values2, count2);
	ft_list_merge(&list1, list2);
	cur = list1;
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
