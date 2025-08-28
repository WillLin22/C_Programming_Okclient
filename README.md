这个库来源于https://github.com/okpy/ok-client.git ，为C语言课程而开发，由于仅需其部分功能（且不满于源项目等同于无的文档和注释）而新开的库。继承了主体结构但有修改。

## 环境

要构建环境，切换到项目目录并运行：

```
shell

conda env create -f conda_env.yml

conda activate okpy

```

## 出题指北

整体框架如下：

```
tests/
    - q1.py
    - q2.py
    - ...
*.ok
ok
```

其中，*.ok为配置文件，在本项目中至少需要包含name和tests两个字段。tests内可有任意多项，key对应tests文件夹中的题目文件名，value项目前仅支持ok_test类型。

对于tests文件夹中的出题文件，示例框架如下：

```
python

test = {
  'name': 'q1',
  'points': 1,
  'suites': [
    {
      'cases': [
        {
          'answer': 'somechoice',
          'choices': [
            'choice0',
            'choice1'
          ],
          'question': r"""
            question
          """
        },
        {
            ...
        }
      ],
      'scored': True,
      'type': 'concept'
    }
  ]
}

```

请注意，填写answer字段时需要填写正确的choice的字符串而非填写abcd或0123等。

文件需如上出题出好，然后在打包成zip发给学生之前需先运行`python ok --lock`，这将会修改上述内容大致如下：

```
python

test = {
  'name': 'q1',
  'points': 1,
  'suites': [
    {
      'cases': [
        {
          'answer': '87dc6f3622a7f346c1413c4449c5cbc2',
          'choices': [
            'choice1',
            'choice2'
          ],
          'hidden': False,
          'locked': True,
          'multiline': False,
          'question': r"""
            question
          """
        },
        {
            ...
        }
      ],
      'scored': True,
      'type': 'concept'
    }
  ]
}
```

具体细节详见本项目中一个简单示例


## 版本信息与（或许有的）更新 

v1.0.0：

目前支持的test类型：

- ok_test的concept，目前仅支持选择题

目前支持的功能：

- 解密（-u）
- 加密（--lock）

目前暂时还不支持但想添加的功能：

- 提交（--submit），实现将完成了的任务打包成一个加密文件并上交
- 解包，方便快速检查同学上交文件
- 打分功能，即用上
- 选择题目功能（-q），目前暂时还不知道能不能用
- 打包该项目的setuptools