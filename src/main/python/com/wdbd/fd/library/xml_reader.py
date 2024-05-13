import xml.etree.ElementTree as ET

# 给定的XML字符串
# xml_string = '''
# <w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"> 
#   <w:pPr>
#     <w:pStyle w:val="Heading1"/>
#     <w:spacing w:line="276"/>
#   </w:pPr>
# </w:p>
# '''

xml_string = '''
<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:pPr>
    <w:pStyle w:val="shimo heading 1"/>
    <w:spacing w:line="276"/>
  </w:pPr>
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="Microsoft YaHei" w:hAnsi="Microsoft YaHei" w:cs="Microsoft YaHei" w:eastAsia="Microsoft YaHei"/>
      <w:color w:val="000000"/>
      <w:rtl w:val="0"/>
    </w:rPr>
    <w:t>一、1111</w:t>
  </w:r>
</w:p>
'''


# xml_string = '''
# <w:pStyle w:val="Heading1"/>
# '''

t_str = "<w:pStyle w:val=\""
start = xml_string.find(t_str) + len(t_str)
print(start)
end = xml_string.find("\"", start+1)
print(end)
print(xml_string[start: end])



# # 解析XML字符串
# root = ET.fromstring(xml_string)

# # 注册命名空间前缀
# ET.register_namespace('w', 'http://schemas.openxmlformats.org/wordprocessingml/2006/main')

# # 找到w:pStyle元素
# p_style = root.find('.//w:pStyle')

# # 获取w:val属性的值

# if p_style is not None:
#     p_style_val = p_style.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
#     print(p_style_val)
# else:
#     pass
