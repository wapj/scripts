# chef cheat sheet

- knife solo 여러 node에 한번에 실행하기

```
$ echo user@server1 user@server2 user@server3 | xargs -n 1 knife solo [prepare|cook|bootstrap]
```
