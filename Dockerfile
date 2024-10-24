FROM odoo:17.0

# Switch to root user temporarily to execute apt-get commands
USER root

# Install additional packages using pip
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
# Switch back to odoo user
USER odoo
