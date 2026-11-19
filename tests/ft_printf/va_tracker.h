/* Force-included in a scratch build: the macros compile away, so only counting
   them at the call site can show whether each va_list was closed. */
#ifndef CLAUDENETTE_VA_TRACKER_H
# define CLAUDENETTE_VA_TRACKER_H

# include <stdarg.h>

extern int h_va_open;

# undef va_start
# undef va_copy
# undef va_end
# define va_start(ap, last) ((void)(__builtin_va_start(ap, last), h_va_open++))
# define va_copy(dest, src) ((void)(__builtin_va_copy(dest, src), h_va_open++))
# define va_end(ap) ((void)(__builtin_va_end(ap), h_va_open--))

#endif
