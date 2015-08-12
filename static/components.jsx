var UpdateElement = React.createClass({
    render: function() {
        alert(this.props.handler);
        return (<form onSubmit={this.props.handler}> 
            {this.props.children} 
            <input type="submit"/>
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

function fetch_and_set_content(baseurl) {
    return function() {
        var url = baseurl + this.props.uid;
        $.ajax({
            url: url,
            success: function(data) {
                this.setState(data);
            }.bind(this)
        });
    }
}

var ProdBox = React.createClass({
    fetchcontent: fetch_and_set_content('/importapi/prod/'),
    altercontent: function(){
        var url = '/importapi/prod/' + this.props.uid;
        $.ajax({
            url: url,
            method: 'PUT',
            data: JSON.stringify(this.state),
            success: function(data) {
                alert('success');
            }
        });
    },
    submit: function(e) {
        e.preventdefault();
        this.altercontent();
    },
    getInitialState: function() {
        this.fetchcontent();
        return {"name_es": 2, "name_zh": 2};
    },
    handler: function(key, event) {
        var newstate = {};
        newstate[event.target.name] = event.target.value;
        this.setState(newstate);
    },
    render: render_input_for_keys(["name_es", "name_zh", "providor_zh", "providor_item_id"]),
});

var PurchaseHeader = React.createClass({
    getInitialState: function() {
        this.fetchcontent();
        return {uid: 1, total_rmb: 100};
    },
    handler: function(key, event) {
    },
    fetchcontent: fetch_and_set_content('/importapi/purchase/'),
    render: render_input_for_keys(['timestamp', 'uid', 'total_rmb', 'providor'])
});

var Purchase = React.createClass({
    getInitialState: function() {
        this.fetchcontent();
        return {items: []};
    },
    fetchcontent: function() {
        var url = '/importapi/purchaseitem?purchase_id=' + this.props.uid;
        $.ajax({
            url: url,
            success: function(data) {
                this.setState({items: data.result});
            }.bind(this)
        });
    },
    render: function() {
        var all_rows = this.state.items.map(function(i) {
            return (<tr>
                <td>{i.upi}</td>
                <td>{i.quantity}</td>
                <td>{i.price_rmb}</td>
                <td>{i.quantity * i.price_rmb}</td>
            </tr>);
        });
        return (
            <div> 
            <PurchaseHeader uid={this.props.uid} />
            <table>
                <tr>
                    <td>Id</td>
                    <td>{"数量"}</td>
                    <td>{"价格"}</td>
                    <td>{"总价"}</td>
                </tr>
                {all_rows}
            </table>
            </div>
        );
    }
});

