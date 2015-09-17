
function query(url, callback) {
    $.ajax({
        url: url,
        success: callback
    });
}

function fetch_and_set_content(baseurl, callback) {
    return function(uid) {
        var url = baseurl + uid;
        query(url, callback);
    }
}

function setState(x) {
    this.setState(x);
}

// Ui form to create an object. 
// Creation triggered by POSTing to an url
// props: url <- where to post
//        names <- what are the names for the inputs
//        update <- used for update
//        uid <- if is update, the id of the element to be updated
//        callback <- call with updated version

var CreateOrUpdateBox = React.createClass({
    fetchnew: function() {
        query(this.props.url + '/' + this.props.uid,
            setState.bind(this));
    },
    getInitialState: function() {
        var x = {};
        this.props.names.forEach(function(name) {
            x[name] = '';
        });
        var update = this.props.update || false;
        if (update) {
            query(this.props.url + '/' + this.props.uid,
                  setState.bind(this));
        }
        return x;
    }, 
    onchange: function(event) {
        var newstate = {};
        newstate[event.target.name] = event.target.value;
        this.setState(newstate);
    },
    submit: function(event) {
        event.preventDefault();
        var url = this.props.url;
        var method = 'POST';
        if (this.props.update) {
            method = 'PUT';
            url = this.props.url + '/' + this.props.uid;
        }
        this.props.callback(this.state);
        $.ajax({
            url: url,
            method: method,
            data: JSON.stringify(this.state),
            success: function(data) {
                this.setState({});
            }.bind(this)
        });
    },
    render: function() {
        console.log(this.state);
        var inputs = this.props.names.map(function(name) {
            return <p> {name}: <input name={name} ref={name}
                value={this.state[name] || ''}
                onChange={this.onchange}/></p>;
        }.bind(this));
        var value = this.props.update ? 'update' : 'create';
        return (<form onSubmit={this.submit}>
            {inputs}
            <input type="submit" value={value}/>
        </form>);
    }
});

function render_input_for_keys(keys, classes) {
    return function() {
        var values = keys.map(function(name) {
            return (
                <p>
                {name}:
                <input name={name} ref={name}
                value={this.state[name]}
                onChange={this.handler.bind(this, name)}/>
                </p>
                );
        }.bind(this));
        return (<div class={classes}>
            {values}
            </div>);
    }
}



function display_list_of_item(names) {
    var list = {
        render: function() {
            var lists = this.props.list.map(function(i) {
                var innerhtml = '';
                for (var x in names) {
                    innerhtml += (' ' + i[names[x]]);
                }
                return <li> {innerhtml} </li>;
            });
            return (<ul>{lists}</ul>);
        }
    };
    return list;
}

// props input:
//   items: an array of items to be displayed
//   name: name of the select field
//   size: size of select field
//   callback: if an item is selected, callback is called with it.
//   itemdisplay: how ot display the item given in items.
var SelectBox = React.createClass({
    getInitialState: function() {
        return {'current': '0'};
    },
    onchange: function(event) {
        this.setState({current: event.target.value});
        var index = parseInt(event.target.value);
        console.log(this.props.callback);
        if (this.props.callback != null) {
            console.log('here');
            this.props.callback(this.props.items[index]);
        }
    },
    render: function() {
        var display = this.props.itemdisplay;
        var items = this.props.items.map(function(i, index) {
            return <option value={index}>{display(i)}</option>;
        });
        return (<select size={this.props.size} value={this.state.current} 
                        onChange={this.onchange} name={this.props.name}>
            {items}
        </select>);
    }
});

module.exports.CreateOrUpdateBox = CreateOrUpdateBox;
module.exports.fetch_and_set_content = fetch_and_set_content;
module.exports.display_list_of_item = display_list_of_item;
module.exports.SelectBox = SelectBox;
module.exports.query = query;
