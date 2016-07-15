# scripts
내가 사용하는 스크립트들

## 설치관련

### install golang

golang 설치~

`apt-get`으로 설치하는 경우 1.2가 깔리니 안까는게 좋음.


```
$ install_golang.sh
```


### install mariadb 10.1 on ubuntu(14.04)

우분투(14.04)버전에서 mariadb를 설치하는 스크립트이다. 
[mariadb home](https://downloads.mariadb.org/mariadb/repositories/#mirror=kaist&distro=Ubuntu&distro_release=trusty--ubuntu_trusty&version=10.1)에서 가져왔다.

```
$ install_mariadb_ubuntu.sh
```

### install_mysql-python.sh

`MySQL-python`이라는 모듈을 설치하기 위한 스크립트이다.
mariadb에 설치할 때 에러가 많이 난다.
설치가 짜증나서 갈아탈까 하다가도, 설치만 되면 쓰기 편해서 그냥 쓰고 있다. 


```
$ install_mysql-python.sh
```


### install_mysqlclient_for_python.sh 

python3에서 mysql client를 설치하는 스크립트이다. `PyMySQL`사용하면 `pip`만 하면 되지만, 느리다. 
그래서 C의 그것을 래핑한 `mysqlclient`를 사용한다. 설치법이 귀찮으므로 스크립트 작성해둠.

홈페이지는 여기니깐 사용법을 모르겠으면 들어가보셈.
[mysqlclient](https://github.com/PyMySQL/mysqlclient-python)

```
$ install_mysqlclient_for_python.sh
```

### install_pyenv.sh 
ubuntu 14.04에서 pyenv를 설치하는게 귀찮아서 만듬
설치하고 나서 `pyenv install 3.5.2` 요런거는 해줘야한다. 

```
$ install_pyenv.sh
```

### install_powerdns.sh

사설 dns서버로 너무 잘쓰고 있는 powerdns라는 녀석이다. mysql을 백엔드로 사용할 수 있다. mysql을 먼저 설치하고 디비도 만들고 테이블도 만들어 줘야한다. 같은 폴더에 `powerdns_init.sql`파일이 있어야만 작동한다. 

사용법은 심플하다. 

mysql을 설치하기위해 이것저것 물어보니 알아서 잘 대답하자. 

```
$ install_powerdns.sh
```

## git관련

### push.sh
내용 수정하고 add commit push 를 세번이나 쳐야되는게 귀찮아서 만듦.

#### usage
```
$ push.sh -m "커밋메세지를 적으삼"
```

### git/initial_push.sh
저장소 처음만들때 해야되는일 귀찮아서 만듦

#### usage

```
$ initial_push.sh user@repository_url
```

### git/apply_git_ignore.sh
git ignore 적용하는 스크립트

#### usage

```
$ apply_git_ignore.sh
```

## Docker관련

### docker/docker_registry_cmd.sh

#### usage

**컨테이너리스트 보기**
```
$ docker_registry_cmd.sh catalog
```


**특정컨테이너의 태그리스트 보기**
```
$ docker_registry_cmd.sh list [컨테이너명]
```

## Virtualbox 관련

### install/install_virtualbox_guest.sh

#### Usage

없음..그냥 실행하면됨.

```
$ install_virtualbox_guest.sh
```

만약에 자동화를 하고 싶다면, chef나 ansible 같은것을 쓰는게 좋을것 같다.

vagrant의 provision기능을 써보려했으나, 실패함.

## 안드로이드

### remove_android.sh
mac에 안드로이드 sdk를 설치했더니 19GB를 사용하고 있어서, 싹 지우는 스크립트를 만듬.

#### usage
very 간단
```
$ remove_android.sh
```


