/* Claudenette's driver. read is renamed only in the student's translation units. */
#ifdef read
# undef read
#endif
#include <unistd.h>
#include <stdlib.h>
#include <fcntl.h>
#include <string.h>
#include <errno.h>
#include <stdio.h>
#include <limits.h>
#ifdef GNL_TRACK_MEMORY
# include "../free_tracker.h"
#endif

char *get_next_line(int fd);

#define INPUT_LIMIT 65536
static unsigned char expected[3][INPUT_LIMIT];
static size_t lengths[3];
static size_t offsets[3];
static size_t line_numbers[3];
static int descriptors[3];
static int short_limit;
static int error_after = -1;
static int positive_reads;
static int fail_every_read;
#ifdef GNL_TRACK_MEMORY
static long failure_at = -1;
static int accept_refusal;
#endif
static int failure_observed;

static void fail(const char *message)
{
    write(2, message, strlen(message));
    write(2, "\n", 1);
    exit(1);
}

ssize_t gnl_read(int fd, void *buffer, size_t count)
{
#ifdef GNL_NONPOSITIVE
    /* A nonpositive BUFFER_SIZE leaves no valid read size. A zero-count probe
       is harmless; any other count would write past the student's buffer. */
    if (count)
        fail("read was called with a nonzero count although BUFFER_SIZE <= 0");
#elif defined(BUFFER_SIZE)
    /* The subject: BUFFER_SIZE "will define the buffer size for read()".
       Zero-count probes stay allowed; any other count must be BUFFER_SIZE. */
    if (count && count != (size_t)BUFFER_SIZE)
    {
        char message[128];

        snprintf(message, sizeof(message),
            "read was called with count %lu; every read must request BUFFER_SIZE (%ld) bytes",
            (unsigned long)count, (long)BUFFER_SIZE);
        fail(message);
    }
#endif
    /* Includes zero-count probes such as read(fd, NULL, 0). */
    if (fail_every_read)
    {
        errno = EIO;
        return (-1);
    }
    if (count && error_after >= 0 && positive_reads >= error_after)
    {
        errno = EIO;
        return (-1);
    }
    if (short_limit && count > (size_t)short_limit)
        count = (size_t)short_limit;
    if (count)
        positive_reads++;
    return (read(fd, buffer, count));
}

static void load(int slot, const char *path)
{
    int fd;
    ssize_t count;

    fd = open(path, O_RDONLY);
    if (fd < 0)
        fail("harness could not open its generated input");
    while ((count = read(fd, expected[slot] + lengths[slot],
                INPUT_LIMIT - lengths[slot])) > 0)
        lengths[slot] += (size_t)count;
    close(fd);
    if (count < 0 || lengths[slot] == INPUT_LIMIT)
        fail("harness input is unreadable or exceeds its capacity");
    descriptors[slot] = open(path, O_RDONLY);
    if (descriptors[slot] < 0)
        fail("harness could not open the student's input descriptor");
}

static void check_memory(void)
{
#ifdef GNL_TRACK_MEMORY
    h_check_redzones();
    if (h_alloc_live())
        fail("allocated memory remains after EOF or an error");
#endif
}

static void wrong_byte(int slot, size_t position, unsigned char wanted,
    unsigned char actual)
{
    char message[160];

    snprintf(message, sizeof(message),
        "line %lu, byte %lu: expected 0x%02x, got 0x%02x",
        (unsigned long)line_numbers[slot] + 1, (unsigned long)position + 1,
        (unsigned int)wanted, (unsigned int)actual);
    fail(message);
}

static int next_line(int slot)
{
    char *line;
    size_t length;
    size_t index;

    line = get_next_line(descriptors[slot]);
#ifdef GNL_TRACK_MEMORY
    h_check_redzones();
    if (failure_at >= 0 && h_alloc_attempts() > failure_at)
    {
        if (line)
            fail("allocation failure must return NULL");
        failure_observed = 1;
        return (0);
    }
    if (accept_refusal && h_alloc_largest() > (unsigned long)SSIZE_MAX)
        fail("an allocation size overflowed: a negative int was converted to size_t");
    if (!line && accept_refusal && h_alloc_refused()
        && offsets[slot] < lengths[slot])
    {
        /* The arena cannot hold the requested buffer: NULL is the right
           answer, and the session's memory check still applies. */
        failure_observed = 1;
        return (0);
    }
    if (line && !h_alloc_owned(line))
        fail("the returned line is not a live, independently freeable allocation");
#endif
    if (offsets[slot] == lengths[slot])
    {
        if (line)
            fail("EOF must return NULL, including on repeated calls");
        return (0);
    }
    if (!line)
        fail("returned NULL before the next complete line");
    length = 0;
    while (offsets[slot] + length < lengths[slot])
    {
        length++;
        if (expected[slot][offsets[slot] + length - 1] == '\n')
            break ;
    }
    index = 0;
    while (index < length)
    {
        if ((unsigned char)line[index] != expected[slot][offsets[slot] + index])
            wrong_byte(slot, index, expected[slot][offsets[slot] + index],
                (unsigned char)line[index]);
        index++;
    }
    if (line[length] != '\0')
        fail("line must end with a zero byte immediately after its contents");
    offsets[slot] += length;
    line_numbers[slot]++;
    free(line);
    return (1);
}

static void session(int files)
{
    int active;
    int slot;

    active = 1;
    while (active && !failure_observed)
    {
        active = 0;
        slot = 0;
        while (slot < files && !failure_observed)
            active |= next_line(slot++);
    }
    if (!failure_observed)
    {
        slot = 0;
        while (slot < files)
            next_line(slot++);
    }
    check_memory();
}

static void pipe_input(int use_stdin)
{
    int ends[2];
    ssize_t written;

    if (pipe(ends) < 0)
        fail("harness could not create a pipe");
    written = write(ends[1], expected[0], lengths[0]);
    if (written < 0 || (size_t)written != lengths[0])
        fail("harness could not fill its small pipe input");
    close(descriptors[0]);
    descriptors[0] = ends[0];
    if (use_stdin)
    {
        if (dup2(ends[0], STDIN_FILENO) < 0)
            fail("harness could not connect stdin");
        close(ends[0]);
        descriptors[0] = STDIN_FILENO;
    }
    /* Every complete line already sent must return while the writer stays open,
       including a second newline held in the student's pending buffer. */
    while (memchr(expected[0] + offsets[0], '\n', lengths[0] - offsets[0]))
        next_line(0);
    close(ends[1]);
    session(1);
}

int main(int argc, char **argv)
{
    int files;
    int slot;
    char *line;
#ifdef GNL_TRACK_MEMORY
    char number[48];
    int size;
#endif

    if (argc < 3)
        fail("harness needs a scenario and an input path");
    files = (!strcmp(argv[1], "multi") || !strcmp(argv[1], "multi_error")) ? 3 : 1;
    if (argc < files + 2)
        fail("harness needs one input per descriptor");
    for (slot = 0; slot < files; slot++)
        load(slot, argv[slot + 2]);
    if (!strcmp(argv[1], "short") || !strcmp(argv[1], "multi_error"))
        short_limit = 3;
    if (!strcmp(argv[1], "read_error") || !strcmp(argv[1], "pending_error")
        || !strcmp(argv[1], "next_call_error"))
    {
        short_limit = 3;
        error_after = 2;
    }
#ifdef GNL_TRACK_MEMORY
    if (!strcmp(argv[1], "allocation_failure"))
    {
        if (argc < 4)
            fail("harness needs the failed allocation index");
        failure_at = strtol(argv[3], NULL, 10);
    }
    accept_refusal = !strcmp(argv[1], "oversized");
    h_alloc_begin(failure_at);
#endif
    if (!strcmp(argv[1], "pending_error"))
    {
        error_after = -1;
        next_line(0);
        error_after = positive_reads + 2;
    }
    if (!strcmp(argv[1], "next_call_error"))
    {
        /* One line returned, a partial line pending: then every read fails,
           including a zero-count probe. NULL must clear the pending input, so
           the same descriptor number, reopened, starts again from byte one. */
        error_after = -1;
        next_line(0);
        fail_every_read = 1;
        line = get_next_line(descriptors[0]);
        if (line)
            fail("a read error at the start of a call must return NULL");
        check_memory();
        fail_every_read = 0;
        slot = open(argv[2], O_RDONLY);
        if (slot < 0 || dup2(slot, descriptors[0]) < 0)
            fail("harness could not reopen its input on the same descriptor");
        close(slot);
        offsets[0] = 0;
        line_numbers[0] = 0;
        short_limit = 0;
        session(1);
    }
    else if (!strcmp(argv[1], "multi_error"))
    {
        next_line(1);
        next_line(2);
        error_after = positive_reads + 2;
        line = get_next_line(descriptors[0]);
        if (line)
            fail("a read error on one descriptor must return NULL");
        error_after = -1;
        close(descriptors[0]);
        descriptors[0] = -1;
        offsets[0] = lengths[0];
        session(files);
    }
    else if (!strcmp(argv[1], "pipe") || !strcmp(argv[1], "stdin"))
        pipe_input(!strcmp(argv[1], "stdin"));
    else if (!strcmp(argv[1], "read_error") || !strcmp(argv[1], "pending_error")
        || !strcmp(argv[1], "negative") || !strcmp(argv[1], "huge_fd")
        || !strcmp(argv[1], "closed") || !strcmp(argv[1], "write_only")
        || !strcmp(argv[1], "directory"))
    {
        if (!strcmp(argv[1], "negative"))
            descriptors[0] = -1;
        else if (!strcmp(argv[1], "huge_fd"))
            descriptors[0] = INT_MAX;
        else if (!strcmp(argv[1], "closed"))
            close(descriptors[0]);
        else if (!strcmp(argv[1], "write_only") || !strcmp(argv[1], "directory"))
        {
            close(descriptors[0]);
            descriptors[0] = open(!strcmp(argv[1], "directory") ? "." : argv[2],
                !strcmp(argv[1], "directory") ? O_RDONLY : O_WRONLY);
            if (descriptors[0] < 0)
                fail("harness could not prepare an invalid read descriptor");
        }
        line = get_next_line(descriptors[0]);
        if (line)
            fail("read errors and invalid descriptors must return NULL");
        check_memory();
    }
    else if (!strcmp(argv[1], "nonpositive"))
    {
        /* Every call returns NULL, repeatedly, without reading or leaking. */
        for (slot = 0; slot < 3; slot++)
        {
            line = get_next_line(descriptors[0]);
            if (line)
                fail("BUFFER_SIZE <= 0 must return NULL on every call");
            check_memory();
        }
    }
    else
        session(files);
#ifdef GNL_TRACK_MEMORY
    if (failure_at >= 0 && !failure_observed)
        fail("the requested allocation failure was never exercised");
    h_alloc_stop();
    if (!strcmp(argv[1], "measure"))
    {
        size = snprintf(number, sizeof(number), "%ld\n", h_alloc_attempts());
        write(1, number, (size_t)size);
    }
#endif
    for (slot = 0; slot < files; slot++)
        close(descriptors[slot]);
    return (0);
}
