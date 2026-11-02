#include <stdlib.h>
#include <unistd.h>
#include "../../free_tracker.h"
#include "libft.h"

t_list *ft_lstmap(t_list *lst, void *(*f)(void *), void (*del)(void *));
size_t ft_strlen(const char *s);

static int g_mode;
static int g_calls;
static int g_deletes;
static void *g_results[3];

static void del(void *content)
{
	g_deletes++;
	free(content);
}

static void *map(void *content)
{
	char *src = content;
	char *out;
	size_t i;

	if (g_mode == 1)
		out = content;
	else if (g_mode == 2)
		out = NULL;
	else
	{
		out = malloc(ft_strlen(src) + 1);
		if (!out)
			return (NULL);
		i = 0;
		while (src[i])
		{
			out[i] = src[i] - 32;
			i++;
		}
		out[i] = '\0';
	}
	if (g_calls < 3)
		g_results[g_calls] = out;
	g_calls++;
	return (out);
}

/* The callback owns the meaning of its return: identity and NULL are valid.
 * The library must always allocate NEW NODES, preserve every source link and
 * content, and store exactly the callback's result (Part 3 of subject 19.3). */
int main(int argc, char **argv)
{
	char values[3][3] = {"ab", "cd", "ef"};
	t_list nodes[3];
	t_list *mapped;
	t_list *walk;
	t_list *next;
	int i;
	int j;

	g_mode = argc > 1 ? atoi(argv[1]) : 0;
	for (i = 0; i < 3; i++)
	{
		nodes[i].content = values[i];
		nodes[i].next = i == 2 ? NULL : &nodes[i + 1];
	}
	h_alloc_begin(-1);
	mapped = ft_lstmap(g_mode == 3 ? NULL : nodes, map, del);
	h_alloc_stop();
	if (g_mode == 3)
	{
		if (mapped || g_calls || h_alloc_live())
			return (write(1, "BAD EMPTY LIST", 14), 0);
		return (write(1, "EMPTY", 5), 0);
	}
	walk = mapped;
	for (i = 0; i < 3; i++)
	{
		if (!walk || !h_alloc_owned(walk) || walk->content != g_results[i])
			return (write(1, "BAD NODE OR CONTENT", 19), 0);
		for (j = 0; j < 3; j++)
			if (walk == &nodes[j])
				return (write(1, "REUSED SOURCE NODE", 18), 0);
		write(1, "[", 1);
		if (walk->content)
			write(1, walk->content, ft_strlen(walk->content));
		write(1, "]", 1);
		walk = walk->next;
	}
	if (walk || g_calls != 3 || g_deletes)
		return (write(1, "BAD CALLBACKS OR TAIL", 21), 0);
	for (i = 0; i < 3; i++)
	{
		if (nodes[i].content != values[i]
			|| nodes[i].next != (i == 2 ? NULL : &nodes[i + 1])
			|| values[i][0] != 'a' + i * 2 || values[i][1] != 'b' + i * 2
			|| values[i][2] != '\0')
			return (write(1, "MUTATED SOURCE", 14), 0);
	}
	walk = mapped;
	while (walk)
	{
		next = walk->next;
		if (g_mode == 0)
			free(walk->content);
		free(walk);
		walk = next;
	}
	if (h_alloc_live())
		return (write(1, "LEAK", 4), 0);
	h_check_redzones();
	write(1, "|NEW|SOURCEOK|FREED", 19);
	return (0);
}
