#!/bin/bash

set -e

git clone https://github.com/b3dk7/StegExpose.git /tmp/StegExpose

cp /tmp/StegExpose/StegExpose.jar /usr/share/StegExpose.jar

rm -rf /tmp/StegExpose

cat << EOF > /usr/bin/stegexpose
#!/bin/sh
java -jar /usr/share/StegExpose.jar \$@
EOF
chmod +x /usr/bin/stegexpose