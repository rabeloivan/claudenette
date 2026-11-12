/* The oracle and the student's library share the same object-pointer addresses. */
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <limits.h>
#include <sys/mman.h>
#include <sys/uio.h>
#include <errno.h>
#ifdef PF_TRACK_MEMORY
# include "../free_tracker.h"
#endif

int ft_printf(const char *format, ...);
static char h_objects[64];
static char *h_string;
static char h_expected[32768];
static size_t h_used;
static int (*h_call)(const char *, ...);
static ssize_t h_write_left = -1;

static void test_unavailable(const char *reason)
{
    fprintf(stderr, "CLAUDENETTE_TEST_UNAVAILABLE: %s\n", reason);
    exit(90);
}

/* Interpose the archive's write calls. writev with one buffer preserves normal
   writes without a platform-specific dynamic-linker hook or extra library. */
ssize_t write(int fd, const void *buffer, size_t count)
{
    struct iovec vector;
    ssize_t written;

    if (fd == STDOUT_FILENO && count && h_write_left >= 0)
    {
        if (!h_write_left)
        {
            errno = EIO;
            return (-1);
        }
        if (count > (size_t)h_write_left)
            count = (size_t)h_write_left;
    }
    vector.iov_base = (void *)buffer;
    vector.iov_len = count;
    written = writev(fd, &vector, 1);
    if (fd == STDOUT_FILENO && h_write_left >= 0 && written > 0)
        h_write_left -= written;
    return (written);
}

static void protect_string(size_t length, int terminated)
{
    long page = sysconf(_SC_PAGESIZE);
    size_t size = length + (size_t)terminated;
    size_t readable;
    char *mapping;

    if (page <= 0)
        test_unavailable("cannot determine the page size for guarded strings");
    if (!size)
        exit(90);
    readable = (size + (size_t)page - 1) / (size_t)page * (size_t)page;
    mapping = mmap(NULL, readable + (size_t)page, PROT_READ | PROT_WRITE,
        MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (mapping == MAP_FAILED)
        test_unavailable("cannot allocate guarded string pages");
    h_string = mapping + readable - size;
    for (size_t index = 0; index < length; index++)
        h_string[index] = (char)('a' + index % 26);
    if (terminated)
        h_string[length] = 0;
    if (mprotect(mapping, readable, PROT_READ) < 0
        || mprotect(mapping + readable, (size_t)page, PROT_NONE) < 0)
        test_unavailable("cannot protect guarded string pages");
}

static int reference_printf(const char *format, ...)
{
    va_list arguments;
    int count;

    va_start(arguments, format);
    count = vsnprintf(h_expected + h_used, sizeof(h_expected) - h_used, format, arguments);
    va_end(arguments);
    if (count < 0 || (size_t)count >= sizeof(h_expected) - h_used)
        test_unavailable("the libc oracle cannot represent the expected output");
    h_used += (size_t)count;
    return (count);
}

#include "cases.h"

int main(int argc, char **argv)
{
    int index;
    int actual_fd;
    int expected_fd;
    int saved_stdout;
    int expected_return;
    int actual_return;
    int repeats;
    int error_mode;
    long failure;
    long attempts = 0;
    int live = 0;
    char metadata[256];
    int size;

    (void)h_objects;
    (void)h_string;
    (void)protect_string;
    if (argc != 7)
        return (90);
    index = atoi(argv[1]);
    prepare_case(index);
    error_mode = !strcmp(argv[4], "write_error");
    failure = strtol(argv[5], NULL, 10);
    repeats = atoi(argv[6]);
    h_call = reference_printf;
    expected_return = invoke_case(index);
    for (int repeat = 1; repeat < repeats; repeat++)
        invoke_case(index);
    expected_fd = open(argv[3], O_WRONLY | O_CREAT | O_TRUNC, 0600);
    actual_fd = open(argv[2], O_WRONLY | O_CREAT | O_TRUNC, 0600);
    saved_stdout = dup(STDOUT_FILENO);
    if (expected_fd < 0 || actual_fd < 0 || saved_stdout < 0)
        test_unavailable("cannot open output captures or preserve stdout");
    if (write(expected_fd, h_expected, h_used) != (ssize_t)h_used)
        test_unavailable("cannot save the oracle output");
    close(expected_fd);
    if (error_mode)
        close(STDOUT_FILENO);
    else if (dup2(actual_fd, STDOUT_FILENO) < 0)
        test_unavailable("cannot redirect stdout to the output capture");
    close(actual_fd);
    h_call = ft_printf;
    if (!strcmp(argv[4], "late_write_error"))
        h_write_left = 1;
#ifdef PF_TRACK_MEMORY
    h_alloc_begin(failure);
#endif
    actual_return = invoke_case(index);
    for (int repeat = 1; repeat < repeats; repeat++)
    {
        int result = invoke_case(index);
        if (result != expected_return)
            actual_return = result;
    }
    h_write_left = -1;
#ifdef PF_TRACK_MEMORY
    attempts = h_alloc_attempts();
    h_alloc_stop();
    h_check_redzones();
    live = h_alloc_live();
#endif
    if (dup2(saved_stdout, STDOUT_FILENO) < 0)
        test_unavailable("cannot restore stdout after capture");
    close(saved_stdout);
    size = snprintf(metadata, sizeof(metadata), "%d %d %ld %d\n",
        expected_return, actual_return, attempts, live);
    if (write(STDOUT_FILENO, metadata, (size_t)size) != size)
        test_unavailable("cannot report the captured return values");
#ifndef PF_TRACK_MEMORY
    (void)failure;
#endif
    return (0);
}
