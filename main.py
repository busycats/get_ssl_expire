import ssl
import socket
from datetime import datetime

def get_ssl_certificate_expiry(hostname):
    context = ssl.create_default_context()

    # 使用 socket 连接目标主机并在 SSL 握手时获取证书
    try:
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                days_remaining = (expiry_date - datetime.utcnow()).days
                return days_remaining, expiry_date
    except (socket.timeout, socket.error, ssl.SSLError) as e:
        return None, None  # 返回 None 以表示无法获取证书

def check_website_access(hostname, port=80, timeout=5):
    try:
        # 尝试连接到指定的主机和端口
        with socket.create_connection((hostname, port), timeout=timeout):
            return True
    except (socket.timeout, socket.error):
        return False

def check_websites_from_file(file_path):
    results = []  # 用于保存所有结果

    with open(file_path, 'r') as f:
        websites = f.readlines()

    for website in websites:
        hostname = website.strip()  # 去除多余的换行符和空格

        if hostname:
            print(f"检查网址: {hostname}")

            website_info = {'hostname': hostname, 'issues': []}

            # 检查 SSL 证书有效期
            days_remaining, expiry_date = get_ssl_certificate_expiry(hostname)
            if days_remaining is None:
                website_info['issues'].append(f"无法获取证书信息")
            elif days_remaining <= 0:
                website_info['issues'].append(f"证书已过期，过期时间为：{expiry_date}")

            # 检查网站是否可访问
            if not check_website_access(hostname):
                website_info['issues'].append(f"网站无法访问！")

            # 如果有问题，加入结果列表
            if website_info['issues']:
                results.append(website_info)

    return results

if __name__ == '__main__':
    # 替换为你存储网址的文本文件路径
    file_path = 'websites.txt'
    results = check_websites_from_file(file_path)

    # 输出所有有问题的网址
    if results:
        print("\n问题网站列表:")
        for result in results:
            print(f"网址: {result['hostname']}")
            for issue in result['issues']:
                print(f"  - {issue}")
    else:
        print("所有网站都正常！")
