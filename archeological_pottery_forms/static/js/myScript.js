 function drawProfile(object, profile) {

                        {% if object.lip_base_y %}
                            ctx.beginPath();
                            ctx.moveTo(0, {{object.lip_base_y}} );
                            ctx.lineTo(canvas.width*2, {{object.lip_base_y}} );
                            ctx.lineWidth = 3;
                            ctx.strokeStyle = '#ff0000'
                            ctx.stroke();
                        {% endif %}

                        {% if object.neck_base_y %}
                            ctx.beginPath();
                            ctx.moveTo(0, {{object.neck_base_y}} );
                            ctx.lineTo(canvas.width*2, {{object.neck_base_y}} );
                            ctx.lineWidth = 3;
                            ctx.strokeStyle = '#ffb600'
                            ctx.stroke();
                        {% endif %}

                        {% if object.shoulders_base_y %}
                            ctx.beginPath();
                            ctx.moveTo(0, {{object.shoulders_base_y}} );
                            ctx.lineTo(canvas.width*2, {{object.shoulders_base_y}} );
                            ctx.lineWidth = 3;
                            ctx.strokeStyle = '#8ae400'
                            ctx.stroke();
                        {% endif %}

                        {% if object.bottom_y %}
                            ctx.beginPath();
                            ctx.moveTo(0, {{object.bottom_y}} );
                            ctx.lineTo(canvas.width*2, {{object.bottom_y}} );
                            ctx.lineWidth = 3;
                            ctx.strokeStyle = '#005cfe'
                            ctx.stroke();
                        {% endif %}

                        {% if profile %}
                            {% for pixel in profile %}
                                ctx.fillRect({{pixel.x_canvas_middle}}, {{pixel.y}},1,1);
                            {% endfor %}
                        {% endif %}
                    };