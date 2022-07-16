from jinja2 import Template

from helpers.shared import ROOT_PATH, logger, join_path
from helpers.dockerstats import DockerStats
from helpers.serversconnections import ServersConnection


tm = Template(
"""
{%- if failed_all -%}
Усі сервери недоступні або атака не запущена 😢
{%- else -%}
⏱ *Час атаки*: {{ duration }}
📤 *Відправлено трафіку*: {{ traffic }}
🏆 *Чемпіон*: {% for champion in champions %}{{ champion }}{% if (loop.length > 1) and (not loop.last) %}, {% endif %}{% endfor %}
{%- for server in servers -%}
{{ space }}
{{ space }}
💻 *{{ server['name'] }}*
Час атаки: {{ server['duration'] }}
Процесор: {{ server['cpu'] }}%
Оперативна памʼять: {{ server['memory'] }}%
Відправлено трафіку: {{ server['traffic'] }}
{%- endfor -%}
{%- if failed_servers != [] -%}
{{ space }}
{{ space }}
На жаль, ми не змогли зібрати статистику з наступних серверів:
{{ space }}
{%- for server in failed_servers -%}
❌ *{{ server }}*
{%- endfor -%}
{%- endif -%}
{%- endif -%}
"""
)

def show_statistic():
    # Read from CSV file which contains servers info. Most probably it needs
    # to be replaced with the connection to database.
    conn = ServersConnection(join_path(ROOT_PATH, 'data/servers.csv'))
    data_dir, failed_conn = conn.download_stats()
    
    # If all of the connections to servers have failed, 
    # return this to bot and exit.
    if sorted([ s['ip'] for s in conn.servers ]) == sorted(failed_conn):
        logger.error('Failed to connect to all servers')
        render = tm.render(failed_all=True).replace('.', '\.').replace('-', '\-')
        print(render)
        return render

    ds = DockerStats('%s/*.csv*' % data_dir)

    servers = []
    champions_aliases = []
    champions_ips = ds.champions()
    for server in conn.servers:
        if not server['ip'] in failed_conn:
            stats = {
                "name": server['alias'],
                "duration": ds.duration(server['ip']),
                "cpu": ds.cpu_avg(server['ip']),
                "memory": ds.memory_avg(server['ip']),
                "traffic": ds.traffic_max(server['ip'])
            }
            servers.append(stats)
            if server['ip'] in champions_ips:
                champions_aliases.append(server['alias'])

    # Convert IPs to aliases according to CSV files
    failed_servers = []
    for failed_server in failed_conn:
        for server in conn.servers:
            if failed_server == server['ip']:
                failed_servers.append(server['alias'])

    params = {
        "duration": ds.duration(),
        "traffic": ds.traffic_max(),
        "champions": champions_aliases,
        "servers": servers,
        "failed_servers": failed_servers
    }   

    # It's needed to escape some characters to avoid conflicts with MarkdownV2.
    # Theoretically, this list should be extended in order cover all of the possible
    # aliases which user can define.
    render = tm.render(params).replace('.', '\.').replace('-', '\-')

    print(render)
    return render

