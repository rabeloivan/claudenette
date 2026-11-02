/* Allocation campaigns for Piscine constructors. Calls use valid inputs;
 * no libc function is probed outside its manual's argument domain. */
#include <stdlib.h>
#include <unistd.h>
#include "free_tracker.h"

#if defined(TEST_NODE) || defined(TEST_FRONT) || defined(TEST_BACK) || defined(TEST_LIST)
# include "ft_list.h"
t_list *ft_create_elem(void *data);
void ft_list_push_front(t_list **head, void *data);
void ft_list_push_back(t_list **head, void *data);
t_list *ft_list_push_strs(int size, char **strs);
#elif defined(TEST_TREE) || defined(TEST_INSERT)
# include "ft_btree.h"
t_btree *btree_create_node(void *item);
void btree_insert_data(t_btree **root, void *item, int (*cmp)(void *, void *));
#elif defined(TEST_STOCK)
# include "ft_stock_str.h"
struct s_stock_str *ft_strs_to_tab(int ac, char **av);
#endif
#if defined(TEST_DUP)
char *ft_strdup(char *s);
#elif defined(TEST_RANGE)
int *ft_range(int min, int max);
#elif defined(TEST_ULTIMATE)
int ft_ultimate_range(int **range, int min, int max);
#elif defined(TEST_JOIN)
char *ft_strjoin(int size, char **words, char *separator);
#elif defined(TEST_CONVERT)
char *ft_convert_base(char *nbr, char *from, char *to);
#elif defined(TEST_MAP)
int *ft_map(int *tab, int length, int (*f)(int));
static int identity(int n) { return n; }
#endif
#if defined(TEST_INSERT)
static int cmp(void *a, void *b) { (void)a; (void)b; return 0; }
#endif

static void *construct(void)
{
#if defined(TEST_DUP)
	return ft_strdup("allocation");
#elif defined(TEST_RANGE)
	return ft_range(-2, 3);
#elif defined(TEST_ULTIMATE)
	int *out = NULL;
	int count = ft_ultimate_range(&out, -2, 3);
	if ((!out && count != -1) || (out && count != 5))
		write(1, "BAD RANGE STATUS", 16);
	return out;
#elif defined(TEST_JOIN)
	char *words[3] = {"one", "two", "three"};
	return ft_strjoin(3, words, ",");
#elif defined(TEST_CONVERT)
	return ft_convert_base("123", "0123456789", "01");
#elif defined(TEST_MAP)
	int values[3] = {1, 2, 3};
	return ft_map(values, 3, identity);
#elif defined(TEST_STOCK)
	char *words[2] = {"one", "two"};
	return ft_strs_to_tab(2, words);
#elif defined(TEST_NODE)
	return ft_create_elem(NULL);
#elif defined(TEST_FRONT) || defined(TEST_BACK)
	t_list *head = NULL;
# if defined(TEST_FRONT)
	ft_list_push_front(&head, NULL);
# else
	ft_list_push_back(&head, NULL);
# endif
	return head;
#elif defined(TEST_LIST)
	char *words[3] = {"one", "two", "three"};
	return ft_list_push_strs(3, words);
#elif defined(TEST_TREE)
	return btree_create_node(NULL);
#elif defined(TEST_INSERT)
	t_btree *root = NULL;
	btree_insert_data(&root, NULL, cmp);
	return root;
#endif
}

static int release(void *result)
{
#if defined(TEST_STOCK)
	struct s_stock_str *array = result;
	void *blocks[3] = {result, NULL, NULL};
	int i, j, count = 1;
	for (i = 0; i < 2; i++)
	{
		void *base = h_alloc_base(array[i].copy);
		if (!base) return 0;
		for (j = 0; j < count && blocks[j] != base; j++) {}
		if (j == count) blocks[count++] = base;
	}
	/* C08 requires copies, not a separate malloc per copy. */
	for (i = 0; i < count; i++) free(blocks[i]);
	return 1;
#elif defined(TEST_LIST)
	t_list *walk = result;
	t_list *next;
	int count = 0;
	while (walk && count++ < 16)
	{
		if (!h_alloc_owned(walk)) return 0;
		next = walk->next;
		free(walk);
		walk = next;
	}
	return walk == NULL;
#endif
	free(result);
	return 1;
}

int main(void)
{
	void *result;
	long count;
	long fail_at;

	h_alloc_begin(-1);
	result = construct();
	count = h_alloc_attempts();
	h_alloc_stop();
	if (!result || !h_alloc_owned(result) || count < 1 || count > 128)
		return (write(1, "BAD SUCCESS", 11), 0);
	if (!release(result) || h_alloc_live())
		return (write(1, "BAD OWNERSHIP", 13), 0);
	for (fail_at = 0; fail_at < count; fail_at++)
	{
		h_alloc_begin(fail_at);
		result = construct();
		h_alloc_stop();
#if defined(TEST_LIST)
		/* This subject does not specify NULL on failure: a freeable partial
		 * list is accepted, but unreachable allocations are never accepted. */
		if (result && (!h_alloc_owned(result) || !release(result)))
			return (write(1, "BAD PARTIAL LIST", 16), 0);
#else
		if (result) return (write(1, "BAD FAILURE RETURN", 18), 0);
#endif
		if (h_alloc_live()) return (write(1, "BAD FAILURE CLEANUP", 19), 0);
		h_check_redzones();
	}
	h_check_redzones();
	write(1, "OK", 2);
	return 0;
}
