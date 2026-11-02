/* Independently implemented contract campaigns informed by the four Francinette
 * suites. No upstream runtime/UI or allocator-size assumptions are used.
 * Provenance and domain decisions: docs/FRANCINETTE_COVERAGE.md. */
#include <ctype.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#ifndef PISCINE
#include "refs/libft_ref.h"
#else
# if KIND == 7
int FT(char *);
# elif KIND == 10
int FT(char *,char *,unsigned int);
# elif KIND == 11 || KIND == 12
unsigned int FT(char *,char *,unsigned int);
# elif KIND == 37 || KIND == 39 || KIND == 40
char *FT(char *,char *);
# elif KIND == 38 || KIND == 41
char *FT(char *,char *,unsigned int);
# elif KIND == 42
int FT(char *,char *);
# endif
#endif
#include "../free_tracker.h"

static size_t length, offset;
static int layout;
#define CHECK(want, got, what) do { long long w_ = (long long)(want); \
    long long g_ = (long long)(got); if (w_ != g_) { \
    printf("%s: length=%zu offset=%zu layout=%d; expected %lld, got %lld", \
           what,length,offset,layout,w_,g_); return 1; } } while (0)
#define UNUSED __attribute__((unused))

static UNUSED int signof(int n) { return (n>0)-(n<0); }
static UNUSED int bytes_equal(const void *want,const void *got,size_t n) {
    const unsigned char *a=want,*b=got;
    for(size_t i=0;i<n;i++) if(a[i]!=b[i]) {
        printf("buffer: length=%zu offset=%zu; byte %zu expected %02x, got %02x",
               length,offset,i,a[i],b[i]); return 0;
    }
    return 1;
}
struct region { unsigned char *map,*data; size_t page; };
static UNUSED struct region region(size_t size) {
    struct region r; size_t unit=(size_t)sysconf(_SC_PAGESIZE);
    r.page=((size+offset)/unit+1)*unit;
    r.map=mmap(NULL,3*r.page,PROT_NONE,MAP_PRIVATE|MAP_ANON,-1,0);
    if(r.map==MAP_FAILED || size+offset>=r.page ||
       mprotect(r.map+r.page,r.page,PROT_READ|PROT_WRITE)) {
        write(1,"guard page setup failed",23); exit(2);
    }
    unsigned char *start=r.map+r.page;
    memset(start,0x5a,r.page);
    r.data=layout==1 ? start+r.page-size : start+offset;
    return r;
}
static UNUSED void readonly(struct region r) {
    if(mprotect(r.map+r.page,r.page,PROT_READ)) exit(2);
}
static UNUSED void writable(struct region r) {
    if(mprotect(r.map+r.page,r.page,PROT_READ|PROT_WRITE)) exit(2);
}
static UNUSED void release_region(struct region r) { munmap(r.map,3*r.page); }
static UNUSED void search_position(const char *base,const char *match,size_t n) {
    if(!match)printf("NULL");
    else if((uintptr_t)match>=(uintptr_t)base &&
            (uintptr_t)match-(uintptr_t)base<=n)
        printf("offset %zu",(size_t)((uintptr_t)match-(uintptr_t)base));
    else printf("pointer outside string");
}
static UNUSED char *find_bounded(const char *h,const char *n,size_t limit) {
    if(!*n) return (char *)h;
    for(size_t i=0;i<limit && h[i];i++) {
        size_t j=0;
        while(j<limit-i && n[j] && h[i+j] && h[i+j]==n[j]) j++;
        if(!n[j]) return (char *)h+i;
    }
    return NULL;
}

#if (KIND >= 1 && KIND <= 14) || (KIND >= 37 && KIND <= 42)
#if KIND >= 1 && KIND <= 4
static int large_campaign(void) {
    size_t n=length;
    struct region a=region(n),b=region(n);
    for(size_t i=0;i<n;i++)a.data[i]=(unsigned char)(i*37);
    readonly(a);
# if KIND == 1
    CHECK(1,FT(b.data,0x180,n)==b.data,"large fill destination");
# elif KIND == 2
    FT(b.data,n);
# else
    CHECK(1,FT(b.data,a.data,n)==b.data,"large copy destination");
# endif
    for(size_t i=0;i<n;i++) {
# if KIND == 1
        int want=0x80;
# elif KIND == 2
        int want=0;
# else
        int want=(unsigned char)(i*37);
# endif
        if(b.data[i]!=want) { printf("large buffer: byte %zu expected %02x, got %02x",i,want,b.data[i]);return 1; }
    }
    release_region(a);release_region(b);return 0;
}
#endif
static int campaign(void) {
#if KIND >= 1 && KIND <= 4
    if(layout==2)return large_campaign();
#endif
    size_t n=length;
    struct region a=region(KIND<=6?(n?n:1):n+1);
    size_t source_offset=offset;offset=(offset*7+3)%32;
    struct region b=region(KIND<=6?(n?n:1):n+40);offset=source_offset;
    unsigned char *src=a.data,*dst=b.data;
    unsigned char expected[131072];
    if(b.page>sizeof(expected)) { puts("unsupported page size"); return 2; }
    uint32_t state=0x42c0ffeeu;
    for(size_t i=0;i<n;i++) {
        state=state*1664525u+1013904223u;
        src[i]=(unsigned char)(KIND<=6?(i%17?state>>24:0):1+state%255);
    }
    if(KIND>6) src[n]=0;
    memcpy(expected,b.map+b.page,b.page);
    size_t at=(size_t)(dst-(b.map+b.page));
    (void)at;(void)expected;(void)dst;
#if KIND == 1 || KIND == 2
    int fills[]={0,65,128,255,256,300,-1};
    for(size_t c=0;c<sizeof(fills)/sizeof(*fills);c++) {
        memset(b.map+b.page,0x5a,b.page); memset(expected,0x5a,b.page);
# if KIND == 1
        memset(expected+at,fills[c],n);
        CHECK(1,FT(dst,fills[c],n)==dst,"returned destination");
# else
        memset(expected+at,0,n); FT(dst,n);
# endif
        CHECK(1,bytes_equal(expected,b.map+b.page,b.page),"untouched surrounding bytes");
    }
#elif KIND == 3
    readonly(a);
    memcpy(expected+at,src,n);
    CHECK(1,FT(dst,src,n)==dst,"returned destination");
    CHECK(1,bytes_equal(expected,b.map+b.page,b.page),"copy including byte guards");
#elif KIND == 4
    /* Both overlap directions, same address and zero length, at every shift. */
    unsigned char actual[131072], model[131072];
    for(size_t shift=0;shift<33;shift++) for(int direction=0;direction<2;direction++) {
        for(size_t i=0;i<sizeof(actual);i++) actual[i]=(unsigned char)(i*37);
        memcpy(model,actual,sizeof(actual));
        size_t d=64+offset+(direction?shift:0),s=64+offset+(direction?0:shift);
        memmove(model+d,model+s,n);
        CHECK(1,FT(actual+d,actual+s,n)==actual+d,"overlap return pointer");
        CHECK(1,bytes_equal(model,actual,sizeof(model)),"overlap and surrounding bytes");
    }
    readonly(a); memcpy(expected+at,src,n);
    CHECK(1,FT(dst,src,n)==dst,"non-overlap return pointer");
    CHECK(1,bytes_equal(expected,b.map+b.page,b.page),"non-overlap guards");
#elif KIND == 5
    readonly(a);
    for(int c=0;c<512;c++) CHECK(1,FT(src,c,n)==memchr(src,c,n),"first byte match / unsigned conversion");
#elif KIND == 6
    memcpy(dst,src,n);readonly(a);readonly(b);
    CHECK(0,signof(FT(src,dst,n)),"equal byte arrays");
    if(n) {
        for(size_t p=0;p<n;p+=(n/7+1)) {
            writable(b);dst[p]^=0x80;readonly(b);
            CHECK(signof(memcmp(src,dst,n)),signof(FT(src,dst,n)),"unsigned byte comparison");
            CHECK(signof(memcmp(dst,src,n)),signof(FT(dst,src,n)),"reverse unsigned comparison");
            writable(b);dst[p]^=0x80;readonly(b);
        }
    }
    writable(b);dst[0]^=1;readonly(b); CHECK(0,FT(src,dst,0),"zero count ignores differing bytes");
#elif KIND == 7
    readonly(a); CHECK(n,FT((char *)src),"length including high bytes and alignment");
#elif KIND == 8 || KIND == 9
    readonly(a);
    for(int index=0;index<1026;index++) {
        int c=index<512?index:index<1024?511-index:index==1024?INT_MIN:INT_MAX;
        char *got=FT((char *)src,c),*want;
# if KIND == 8
        want=strchr((char *)src,c);
# else
        want=strrchr((char *)src,c);
# endif
        if(got!=want) {
            printf("c=%d byte=0x%02x; expected ",c,(unsigned char)c);
            search_position((char *)src,want,n);printf(", got ");
            search_position((char *)src,got,n);
            return 1;
        }
    }
#elif KIND == 10
    memcpy(dst,src,n+1);readonly(a);readonly(b);
    size_t counts[]={0,n,n+1,SIZE_MAX};
    for(size_t k=0;k<4;k++) {
        CHECK(0,signof(FT((char *)src,(char *)dst,counts[k])),"equal strings stop at NUL");
        if(n) {
            writable(b);dst[n/2]^=0x80;
            if(!dst[n/2]) dst[n/2]=1;
            readonly(b);
            CHECK(signof(strncmp((char *)src,(char *)dst,counts[k])),
                  signof(FT((char *)src,(char *)dst,counts[k])),"unsigned comparison / count boundary");
            writable(b);dst[n/2]=src[n/2];readonly(b);
        }
    }
    struct region left=region(n?n:1),right=region(n?n:1);
    memset(left.data,'a',n?n:1);memset(right.data,'a',n?n:1);readonly(left);readonly(right);
    CHECK(0,FT((char *)left.data,(char *)right.data,n),"bounded arrays without a NUL terminator");
    release_region(left);release_region(right);
#elif KIND == 11 || KIND == 12
    readonly(a);
    size_t sizes[]={0,1,2,3,4,5,11,12,20,n+32};
    for(size_t k=0;k<sizeof(sizes)/sizeof(*sizes);k++) {
        memset(b.map+b.page,0x5a,b.page); strcpy((char *)dst,"pqrstuvwxyz");
        memcpy(expected,b.map+b.page,b.page);
        unsigned char *want=expected+at;
        size_t capacity=sizes[k],answer;
# if KIND == 11
        answer=n;
        if(capacity) { size_t copy=n<capacity-1?n:capacity-1; memcpy(want,src,copy); want[copy]=0; }
# else
        size_t d=0; while(d<capacity && want[d]) d++;
        answer=d+n;
        if(d<capacity) { size_t room=capacity-d-1,copy=n<room?n:room; memcpy(want+d,src,copy);want[d+copy]=0; }
# endif
        CHECK(answer,FT((char *)dst,(char *)src,capacity),"attempted length including truncation");
        CHECK(1,bytes_equal(expected,b.map+b.page,b.page),"NUL placement and untouched destination bytes");
    }
# if KIND == 12
    struct region unterm=region(n?n:1);
    memset(unterm.data,'A',n?n:1);readonly(unterm);
    CHECK(n+3,FT((char *)unterm.data,"abc",n),"unterminated destination: bounded read and no write");
    release_region(unterm);
# endif
#elif KIND == 13
    readonly(a);
    char needle[8]; size_t take=n-n/2<3?n-n/2:3; memcpy(needle,src+n/2,take);needle[take]=0;
    /* Clamp extraction for n=1/2 so no byte beyond the source is accessed. */
    take=n-n/2<take?n-n/2:take;needle[take]=0;
    const char *needles[]={"",needle,"XYZXYZ","MZIRIBMZP"};
    size_t limits[]={0,n/2,n,n+1,SIZE_MAX};
    for(size_t j=0;j<4;j++) for(size_t k=0;k<5;k++)
        CHECK(1,FT((char *)src,needles[j],limits[k])==find_bounded((char *)src,needles[j],limits[k]),
              "bounded first match / empty needle / stop at NUL");
#elif KIND == 14
    readonly(a); h_alloc_begin(-1);char *copy=FT((char *)src);h_alloc_stop();
    CHECK(1,copy!=NULL,"allocated duplicate");CHECK(1,h_alloc_owned(copy),"caller-owned duplicate");
    CHECK(1,bytes_equal(src,copy,n+1),"duplicate including NUL");free(copy);
    CHECK(0,h_alloc_live(),"no hidden allocations");
#elif KIND == 37
    readonly(a);memcpy(expected+at,src,n+1);
    CHECK(1,FT((char *)dst,(char *)src)==(char *)dst,"returned destination");
    CHECK(1,bytes_equal(expected,b.map+b.page,b.page),"string, terminator and byte guards");
#elif KIND == 38 || KIND == 41
    readonly(a);size_t counts[]={0,1,n/2,n,n+1,n+16};
    for(size_t k=0;k<sizeof(counts)/sizeof(*counts);k++) {
        memset(b.map+b.page,0x5a,b.page);
# if KIND == 41
        strcpy((char *)dst,"abcde");
# endif
        memcpy(expected,b.map+b.page,b.page);
# if KIND == 38
        strncpy((char *)expected+at,(char *)src,counts[k]);
# else
        strncat((char *)expected+at,(char *)src,counts[k]);
# endif
        CHECK(1,FT((char *)dst,(char *)src,(unsigned)counts[k])==(char *)dst,"returned destination");
        CHECK(1,bytes_equal(expected,b.map+b.page,b.page),"count boundary, NUL/padding and untouched bytes");
    }
#elif KIND == 39
    readonly(a);strcpy((char *)dst,"abcde");memcpy(expected,b.map+b.page,b.page);
    strcat((char *)expected+at,(char *)src);
    CHECK(1,FT((char *)dst,(char *)src)==(char *)dst,"returned destination");
    CHECK(1,bytes_equal(expected,b.map+b.page,b.page),"append and terminator guards");
#elif KIND == 40
    readonly(a);char needle[8];size_t take=n-n/2<3?n-n/2:3;
    memcpy(needle,src+n/2,take);needle[take]=0;
    char empty[]="",missing[]="XYZXYZ";char *needles[]={empty,needle,missing};
    for(size_t k=0;k<3;k++) CHECK(1,FT((char *)src,needles[k])==strstr((char *)src,needles[k]),
                                 "first match / empty needle / protected string boundary");
#elif KIND == 42
    memcpy(dst,src,n+1);readonly(a);
    CHECK(0,signof(FT((char *)src,(char *)dst)),"equal strings");
    if(n) { dst[n/2]^=0x80;if(!dst[n/2])dst[n/2]=1;
        CHECK(signof(strcmp((char *)src,(char *)dst)),signof(FT((char *)src,(char *)dst)),"unsigned character comparison");
        CHECK(signof(strcmp((char *)dst,(char *)src)),signof(FT((char *)dst,(char *)src)),"reverse comparison"); }
#endif
    release_region(a);release_region(b);h_check_redzones();return 0;
}
#elif KIND == 15 || KIND == 16
static unsigned calls; static char *original; static int bad_callback;
static char transform(unsigned i,char c) {
    if(i!=calls || c!=original[i]) bad_callback=1;
    calls++;
    /* Embedded NUL results must not prevent later callbacks. */
    return layout==1 ? (i%3==0?0:(char)(c+i)) : layout==2?'0':(char)(c+i);
}
static UNUSED void transform_at(unsigned i,char *c) {
    if(c!=original+i) bad_callback=1;
    *c=transform(i,*c);
}
static int campaign(void) {
    char source[2048],snapshot[2048],wanted[2048];
    for(size_t i=0;i<length;i++) source[i]=(char)('a'+i%26);
    source[length]=0;memcpy(snapshot,source,length+1);original=source;
    for(size_t i=0;i<length;i++) wanted[i]=layout==1?(i%3==0?0:(char)(source[i]+i)):
                                                     layout==2?'0':(char)(source[i]+i);
    wanted[length]=0;
# if KIND == 15
    h_alloc_begin(-1);char *result=FT(source,transform);h_alloc_stop();
    CHECK(1,result!=NULL,"mapped string");CHECK(1,h_alloc_owned(result),"independent mapped string");
    CHECK(1,bytes_equal(snapshot,source,length+1),"source preserved");
    CHECK(1,bytes_equal(wanted,result,length+1),"mapped bytes including embedded NUL");free(result);
    CHECK(0,h_alloc_live(),"mapped string ownership");
# else
    FT(source,transform_at);
    CHECK(1,bytes_equal(wanted,source,length+1),"characters modified at original addresses");
# endif
    CHECK(length,calls,"one callback per original character");CHECK(0,bad_callback,"callback order/index/address");
    h_check_redzones();return 0;
}
#elif KIND >= 17 && KIND <= 25
static size_t calls; static int bad_callback; static t_list *nodes[1024];static int values[1024];
static unsigned char disposed[1024];
static UNUSED void visit(void *p) {
    if(calls>=length || p!=nodes[calls]->content) bad_callback=1;
    if(p) (*(int *)p)++;
    calls++;
}
static UNUSED void dispose(void *p) {
    /* Clear may release successors first. The subject specifies every
     * content exactly once, not a callback order. NULL contents can repeat. */
    size_t limit=KIND==22?(length?1:0):length;
    size_t i=0;
    while(i<limit && (disposed[i] || p!=(layout==1 && i%3==0?NULL:&values[i]))) i++;
    if(i==limit) bad_callback=1;
    else disposed[i]=1;
    calls++;
}
static UNUSED void *map_content(void *p) {
    if(calls>=length || p!=nodes[calls]->content) bad_callback=1;
    calls++; int *copy=malloc(sizeof(*copy));
    if(copy) *copy=p?*(int *)p+10:10;
    return copy;
}
static int campaign(void) {
    h_alloc_begin(-1);
    for(size_t i=0;i<length;i++) {
        values[i]=(int)i;nodes[i]=malloc(sizeof(t_list));
        if(!nodes[i]) return 2;
        nodes[i]->content=layout==1 && i%3==0?NULL:&values[i];nodes[i]->next=NULL;
        if(i) nodes[i-1]->next=nodes[i];
    }
    t_list *head=length?nodes[0]:NULL; (void)head;
# if KIND == 17
    t_list *node=FT(length?&values[0]:NULL);CHECK(1,node!=NULL,"new node");
    CHECK(1,node->content==(length?&values[0]:NULL),"exact opaque content pointer");
    CHECK(1,node->next==NULL,"next initialized");free(node);
# elif KIND == 18 || KIND == 19
    t_list *node=malloc(sizeof(*node)); if(!node)return 2;
    node->content=NULL;node->next=NULL;
#  if KIND == 18
    FT(&head,node);CHECK(1,head==node,"new head pointer");
    CHECK(1,node->next==(length?nodes[0]:NULL),"original list attached unchanged");
#  else
    t_list *chain=malloc(sizeof(*chain));if(!chain)return 2;chain->content=&values[0];chain->next=NULL;
    node->next=chain;FT(&head,node);
    CHECK(1,head==(length?nodes[0]:node),"head preserved");
    CHECK(1,!length || nodes[length-1]->next==node,"new chain appended");
    CHECK(1,node->next==chain && chain->next==NULL,"new chain preserved");free(chain);
    if(length) nodes[length-1]->next=NULL;
#  endif
    free(node);
# elif KIND == 20
    CHECK(length,FT(head),"unsigned list size");
# elif KIND == 21
    CHECK(1,FT(head)==(length?nodes[length-1]:NULL),"exact final node pointer");
# elif KIND == 22
    if(length) {
        FT(nodes[0],dispose);CHECK(0,h_alloc_owned(nodes[0]),"only selected node freed");
        CHECK(1,calls,"one delete callback");
        for(size_t i=1;i<length;i++) CHECK(1,h_alloc_owned(nodes[i]),"following nodes retained");
        nodes[0]=NULL;
    }
# elif KIND == 23
    FT(&head,dispose);CHECK(1,head==NULL,"head reset");CHECK(length,calls,"delete callback count");
    for(size_t i=0;i<length;i++) CHECK(0,h_alloc_owned(nodes[i]),"every original node freed");
# elif KIND == 24
    FT(head,visit);CHECK(length,calls,"callback count");
    for(size_t i=0;i<length;i++) CHECK(i+(nodes[i]->content!=NULL),values[i],"callback updated original content");
# elif KIND == 25
    /* Mapping must not mutate source content: use a non-mutating adapter. */
    t_list *mapped=FT(head,map_content,free),*walk=mapped;
    CHECK(length,calls,"mapping callback count");
    for(size_t i=0;i<length;i++) {
        CHECK(1,walk!=NULL,"mapped length");CHECK(1,h_alloc_owned(walk),"owned result node");
        for(size_t j=0;j<length;j++) CHECK(1,walk!=nodes[j],"independent result nodes");
        CHECK(1,h_alloc_owned(walk->content),"callback result retained");
        CHECK(nodes[i]->content?(int)i+10:10,*(int *)walk->content,"exact mapped value");
        t_list *next=walk->next;free(walk->content);free(walk);walk=next;
    }
    CHECK(1,walk==NULL,"mapped NULL termination");
# endif
# if KIND != 23
    for(size_t i=0;i<length;i++) if(nodes[i]) {
#  if KIND == 25
        CHECK(i,values[i],"original content preserved");
#  endif
#  if KIND != 22
        CHECK(1,nodes[i]->next==(i+1<length?nodes[i+1]:NULL),"source links preserved");
#  endif
        free(nodes[i]);
    }
# endif
    CHECK(0,bad_callback,"callback arguments and multiplicity");h_alloc_stop();CHECK(0,h_alloc_live(),"all node ownership accounted for");
    h_check_redzones();return 0;
}
#elif KIND >= 26 && KIND <= 29
static int campaign(void) {
    FILE *file=tmpfile();if(!file)return 2;int fd=fileno(file);
    unsigned char expected[8192],actual[8192];size_t used=0;
# if KIND == 26
    for(int c=0;c<256;c++) { FT((char)c,fd); expected[used++]=(unsigned char)c; }
# elif KIND == 27 || KIND == 28
    char text[2048];for(size_t i=0;i<length;i++)text[i]=(char)(1+(i*37)%255);text[length]=0;
    for(int repeat=0;repeat<3;repeat++) {
        FT(text,fd);memcpy(expected+used,text,length);used+=length;
#  if KIND == 28
        expected[used++]='\n';
#  endif
    }
# else
    int numbers[]={0,1,-1,10,-10,10000043,-10000043,INT_MIN,INT_MAX};
    for(size_t i=0;i<sizeof(numbers)/sizeof(*numbers);i++) {
        FT(numbers[i],fd);used+=(size_t)sprintf((char *)expected+used,"%d",numbers[i]);
    }
# endif
    if(lseek(fd,0,SEEK_SET)<0) return 2;
    ssize_t got=read(fd,actual,sizeof(actual));CHECK(used,got,"bytes written to an arbitrary descriptor");
    CHECK(1,bytes_equal(expected,actual,used),"binary descriptor contents / repeated calls");
    fclose(file);return 0;
}
#elif KIND == 43
static int campaign(void) {
    uint32_t state=0x42c0ffeeu;
    int boundaries[]={0,1,-1,9,-9,10,-10,99,-99,100,-100,INT_MAX,INT_MIN};
    for(size_t i=0;i<length+sizeof(boundaries)/sizeof(*boundaries);i++) {
        state=state*1664525u+1013904223u;
        int number=i<sizeof(boundaries)/sizeof(*boundaries)?boundaries[i]:(int)(state%2147483648u);
        if(i>=sizeof(boundaries)/sizeof(*boundaries) && (state&0x80000000u))number=-number;
        char expected[32];snprintf(expected,sizeof(expected),"%d",number);
        h_alloc_begin(-1);char *actual=FT(number);h_alloc_stop();
        CHECK(1,actual!=NULL,"formatted integer");CHECK(1,h_alloc_owned(actual),"owned integer string");
        CHECK(1,bytes_equal(expected,actual,strlen(expected)+1),"integer digits, sign and NUL");
        free(actual);CHECK(0,h_alloc_live(),"integer result cleanup");
    }
    h_check_redzones();return 0;
}
#elif KIND == 44
static int campaign(void) {
    size_t counts[]={0,1,3,37},sizes[]={0,1,length,sizeof(long)};
    for(size_t c=0;c<4;c++)for(size_t s=0;s<4;s++) {
        h_alloc_begin(-1);unsigned char *result=FT(counts[c],sizes[s]);h_alloc_stop();
        CHECK(1,result!=NULL,"calloc including zero-sized requests");
        CHECK(1,h_alloc_owned(result),"freeable calloc result");
        for(size_t i=0;i<counts[c]*sizes[s];i++)CHECK(0,result[i],"all allocated bytes zero");
        free(result);CHECK(0,h_alloc_live(),"calloc ownership");
    }
    CHECK(1,FT(SIZE_MAX,2)==NULL,"multiplication overflow");
    CHECK(1,FT(SIZE_MAX/2+1,2)==NULL,"wrapped multiplication");
    h_check_redzones();return 0;
}
#elif KIND >= 45 && KIND <= 48
static int campaign(void) {
    size_t n=length;
    struct region a=region(n+1);char *source=(char *)a.data;
    for(size_t i=0;i<n;i++) source[i]=(char)(1+(i*37)%255);
    source[n]=0;readonly(a);
    char wanted[4096];
# if KIND == 45
    unsigned starts[]={0,(unsigned)n/2,(unsigned)n,(unsigned)n+1,UINT_MAX};
    size_t counts[]={0,1,n,n+16,SIZE_MAX};
    for(size_t i=0;i<5;i++)for(size_t j=0;j<5;j++) {
        size_t amount=starts[i]<n?n-starts[i]:0;if(amount>counts[j])amount=counts[j];
        if(amount)memcpy(wanted,source+starts[i],amount);
        wanted[amount]=0;
        h_alloc_begin(-1);char *out=FT(source,starts[i],counts[j]);h_alloc_stop();
        CHECK(1,out!=NULL,"substring allocation");CHECK(1,h_alloc_owned(out),"freeable substring");
        CHECK(1,bytes_equal(wanted,out,amount+1),"clamped substring and terminator");
        free(out);CHECK(0,h_alloc_live(),"substring ownership");
    }
# elif KIND == 46
    const char *second[]={"",source,source+n/2};
    for(size_t i=0;i<3;i++) {
        size_t right=strlen(second[i]);memcpy(wanted,source,n);memcpy(wanted+n,second[i],right+1);
        h_alloc_begin(-1);char *out=FT(source,second[i]);h_alloc_stop();
        CHECK(1,out!=NULL,"joined allocation");CHECK(1,h_alloc_owned(out),"independent joined string");
        CHECK(1,bytes_equal(wanted,out,n+right+1),"joined bytes, aliased inputs and NUL");
        free(out);CHECK(0,h_alloc_live(),"join ownership");
    }
# elif KIND == 47
    struct region charset=region(3);char *set=(char *)charset.data;
    set[0]=n?source[0]:'a';set[1]=n?source[n-1]:'b';set[2]=0;readonly(charset);
    size_t first=0,last=n;
    while(first<last && strchr(set,source[first]))first++;
    while(last>first && strchr(set,source[last-1]))last--;
    memcpy(wanted,source+first,last-first);wanted[last-first]=0;
    h_alloc_begin(-1);char *out=FT(source,set);h_alloc_stop();
    CHECK(1,out!=NULL,"trim allocation");CHECK(1,h_alloc_owned(out),"independent trimmed string");
    CHECK(1,bytes_equal(wanted,out,last-first+1),"trimmed edges, high bytes and preserved middle");
    free(out);CHECK(0,h_alloc_live(),"trim ownership");release_region(charset);
# else
    (void)wanted;
    char separators[]={0,n?source[0]:'a',n?source[n/2]:'b',n?source[n-1]:'c'};
    for(size_t c=0;c<4;c++) {
        h_alloc_begin(-1);char **out=FT(source,separators[c]);h_alloc_stop();
        CHECK(1,out!=NULL,"split allocation");CHECK(1,h_alloc_owned(out),"freeable split array");
        size_t i=0,word=0;
        while(i<n) {
            while(i<n && source[i]==separators[c])i++;
            if(i==n)break;
            size_t start=i;while(i<n && source[i]!=separators[c])i++;
            CHECK(1,out[word]!=NULL,"all split words present");CHECK(1,h_alloc_owned(out[word]),"separately freeable word");
            CHECK(1,bytes_equal(source+start,out[word],i-start),"split word bytes");
            CHECK(0,out[word][i-start],"word terminator");word++;
        }
        CHECK(1,out[word]==NULL,"array NULL terminator");
        for(size_t i=0;i<word;i++)free(out[i]);
        free(out);CHECK(0,h_alloc_live(),"split ownership");
    }
# endif
    release_region(a);h_check_redzones();return 0;
}
#elif KIND == 49
static int campaign(void) {
    char input[32];
    for(int c=0;c<=255;c++) {
        input[0]=(char)c;snprintf(input+1,sizeof(input)-1," %d",c+1);
        offset=(size_t)c;CHECK(atoi(input),FT(input),"all leading byte values / whitespace / first digit");
    }
    return 0;
}
#else
#error Unknown campaign kind
#endif
int main(int argc,char **argv) {
    length=argc>1?(size_t)strtoul(argv[1],NULL,10):0;
    offset=argc>2?(size_t)strtoul(argv[2],NULL,10):0;
    layout=argc>3?atoi(argv[3]):0;
    size_t maximum=KIND>=1 && KIND<=4 && layout==2?128UL*1024*1024:
                   (KIND<=14 || (KIND>=37 && KIND<=42))?65536:1024;
    if(length>maximum || offset>31 || layout<0 || layout>2) return 2;
    int result=campaign();
    if(!result)h_check_redzones();
    if(!result)write(1,"OK",2);
    return result;
}
