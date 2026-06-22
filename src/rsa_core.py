def mod_pow(n,e,m,T=None):
    result=1
    n=n%m
    if T:
        e=e%T
    while e:
        if e&1:
            result=(result*n)%m
        n=(n*n)%m
        e>>=1
    return result
def exgcd(a,b):
    x0,y0,x1,y1=1,0,0,1
    while b:
        q=a//b
        a,b=b,a-q*b
        x0,x1=x1,x0-x1*q
        y0,y1=y1,y0-y1*q
    gcd=a
    return gcd,x0,y0#a*x0+b*y0=gcd
def eluer_prime(n):
    not_prime=[0]*(n+1)
    primes=[]
    for i in range(2,n+1):
        if not not_prime[i]:
            primes.append(i)
        for j in primes:
            if i*j>n:
                break
            not_prime[i*j]=1
            if i%j==0:
                break
    return primes
def get_keys(primes):
    import random,math
    p=random.choice(primes)
    while True:
        q=random.choice(primes)
        if p!=q:
            break
    n=p*q
    phi=(p-1)*(q-1)
    while True:
        e=random.randint(3,1000000)
        if math.gcd(e,phi)==1:
            break
    _1,d,_2=exgcd(e,phi)
    return p,q,n,phi,e,d%phi
def crack_n(n, timeout=2.0):
    """返回 (p, q) 或 None（超时则返回None）"""
    import time,math
    start = time.time()
    limit = int(math.isqrt(n))
    for i in range(2, limit + 1):
        if time.time() - start > timeout:
            return None  #超时
        if n % i == 0:
            return i, n // i
    return None