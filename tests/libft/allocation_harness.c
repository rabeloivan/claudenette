/* Subject 19.3: constructors return NULL on allocation failure; allocated
 * partial results must be freed. Each run first measures a successful call,
 * then fails every allocation position without assuming an implementation's
 * allocation count. Callback allocation is outside ft_lstmap's own contract. */
#include <stdlib.h>
#include <unistd.h>
#include "../free_tracker.h"
#include "refs/libft_ref.h"

#if defined(TEST_FT_STRMAPI)
static char identity(unsigned int i, char c)
{
	(void)i;
	return (c);
}
#endif

#if defined(TEST_FT_LSTMAP)
static void *copy_content(void *content)
{
	int *copy;

	h_alloc_pause(1);
	copy = malloc(sizeof(int));
	h_alloc_pause(0);
	if (copy)
		*copy = *(int *)content + 1;
	return (copy);
}
#endif

static void *construct(void)
{
#if defined(TEST_FT_CALLOC)
	return (ft_calloc(8, 4));
#elif defined(TEST_FT_STRDUP)
	return (ft_strdup("allocation campaign"));
#elif defined(TEST_FT_SUBSTR)
	return (ft_substr("allocation campaign", 2, 8));
#elif defined(TEST_FT_STRJOIN)
	return (ft_strjoin("allocation", " campaign"));
#elif defined(TEST_FT_STRTRIM)
	return (ft_strtrim("  allocation campaign  ", " "));
#elif defined(TEST_FT_SPLIT)
	return (ft_split("alpha beta gamma delta", ' '));
#elif defined(TEST_FT_ITOA)
	return (ft_itoa(-2147483647 - 1));
#elif defined(TEST_FT_STRMAPI)
	return (ft_strmapi("allocation campaign", identity));
#elif defined(TEST_FT_LSTNEW)
	return (ft_lstnew(NULL));
#elif defined(TEST_FT_LSTMAP)
	int values[3] = {1, 2, 3};
	t_list nodes[3] = {{&values[0], &nodes[1]},
		{&values[1], &nodes[2]}, {&values[2], NULL}};
	return (ft_lstmap(nodes, copy_content, free));
#endif
}

static int release(void *result)
{
#if defined(TEST_FT_SPLIT)
	char **parts = result;
	int i = 0;
	while (parts[i] && i < 16)
	{
		if (!h_alloc_owned(parts[i]))
			return (0);
		free(parts[i++]);
	}
	if (i == 16)
		return (0);
#elif defined(TEST_FT_LSTMAP)
	t_list *node = result;
	t_list *next;
	int count = 0;
	while (node && count++ < 16)
	{
		if (!h_alloc_owned(node) || !h_alloc_owned(node->content))
			return (0);
		next = node->next;
		free(node->content);
		free(node);
		node = next;
	}
	return (node == NULL);
#endif
	free(result);
	return (1);
}

int main(void)
{
	void *result;
	long attempts;
	long fail_at;

	h_alloc_begin(-1);
	result = construct();
	attempts = h_alloc_attempts();
	h_alloc_stop();
	if (!result || !h_alloc_owned(result) || attempts < 1 || attempts > 128)
		return (write(1, "BAD SUCCESS", 11), 0);
	if (!release(result) || h_alloc_live())
		return (write(1, "BAD OWNERSHIP", 13), 0);
	fail_at = 0;
	while (fail_at < attempts)
	{
		h_alloc_begin(fail_at++);
		result = construct();
		h_alloc_stop();
		if (result || h_alloc_live())
			return (write(1, "BAD FAILURE CLEANUP", 19), 0);
		h_check_redzones();
	}
	h_check_redzones();
	write(1, "OK", 2);
	return (0);
}
