# scripts
내가 사용하는 스크립트들

## 설치관련

### install mariadb 10.1 on ubuntu(14.04)

우분투(14.04)버전에서 mariadb를 설치하는 스크립트이다. 
[mariadb home](https://downloads.mariadb.org/mariadb/repositories/#mirror=kaist&distro=Ubuntu&distro_release=trusty--ubuntu_trusty&version=10.1)에서 가져왔다.

```
$ install_mariadb_ubuntu.sh
```


### install_mysqlclient_for_python.sh 

python3에서 mysql client를 설치하는 스크립트이다. `PyMySQL`사용하면 `pip`만 하면 되지만, 느리다. 
그래서 C의 그것을 래핑한 `mysqlclient`를 사용한다. 설치법이 귀찮으므로 스크립트 작성해둠.

홈페이지는 여기니깐 사용법을 모르겠으면 들어가보셈.
[mysqlclient](https://github.com/PyMySQL/mysqlclient-python)

```
$ install_mysqlclient_for_python.sh
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


