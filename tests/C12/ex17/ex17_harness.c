/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ex17_harness.c                                     :+:      :+:    :+:   */
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

void	ft_sorted_list_merge(t_list **begin_list1, t_list *begin_list2,
			int (*cmp)());

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

int	main(int argc, char **argv)
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
	int		(*cmp)(void *, void *);

	if (h_null_callback_mode(argc, argv))
	{
		values1[0] = 1;
		values1[1] = 3;
		values1[2] = 5;
		list1 = h_build_list(values1, 3);
		values2[0] = 2;
		values2[1] = 4;
		values2[2] = 6;
		list2 = h_build_list(values2, 3);
		ft_sorted_list_merge(&list1, list2, NULL);
		write(1, "OK\n", 3);
		return (0);
	}
	bytes_read = read(0, buffer, 4095);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	if (buffer[0] == 'D')
		cmp = &h_cmp_int_desc;
	else
		cmp = &h_cmp_int_asc;
	pos = 0;
	while (buffer[pos] != '\n')
		pos++;
	pos++;
	pos = read_list(buffer, pos, &count1, values1);
	read_list(buffer, pos, &count2, values2);
	list1 = h_build_list(values1, count1);
	list2 = h_build_list(values2, count2);
	ft_sorted_list_merge(&list1, list2, cmp);
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
